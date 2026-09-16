# Supabase Database Setup

This directory holds the Postgres schema and seed data for the Books Service, designed to run on [Supabase](https://supabase.com).

## Files

- `schema.sql` — table definitions, indexes, triggers, RLS. Idempotent (safe to re-run).
- `seed.sql` — starter customer/business/categories. **Edit this before running** — it's a template, not your real data.

## 1. Create a Supabase Project

1. Go to https://supabase.com/dashboard → New Project
2. Choose a name, database password, and region
3. Wait ~2 minutes for provisioning

## 2. Run the Schema

In the Supabase dashboard:

1. Go to **SQL Editor** → New query
2. Paste the contents of `schema.sql`
3. Click **Run**

This creates:

| Table | Purpose |
|---|---|
| `customers` | Each tenant of this service — typically one Slack workspace |
| `businesses` | Each company/entity a customer tracks books for |
| `accounts` | Bank/credit accounts, each tied to one business |
| `categories` | Bookkeeping categories, scoped to one customer |
| `category_businesses` | Which categories apply to which businesses (within the same customer) |
| `transactions` | The actual transactions to categorize |

## 3. Multi-Tenancy Model

This service supports **multiple customers, each with multiple businesses**:

```
customer (e.g. "Coding Crafts")
├── business "Coding Crafts LLC"
│   ├── account "Chase Business Checking"
│   └── account "Chase Business Ink"
└── business "Side Project Inc"
    └── account "Mercury Checking"

categories (scoped to the customer, shared across its businesses via category_businesses)
```

- **Categories belong to a customer, not globally.** Two different customers never share category rows, even if the names match — each gets its own.
- **Every account belongs to exactly one business**, and every business belongs to exactly one customer. This chain (`account → business → customer`) is how every query scopes data to the right tenant.
- **A Slack workspace maps to one customer** via `customers.slack_team_id`. When a `/run-books` command comes in, the backend looks up the customer by the Slack `team_id` in the request, then runs the entire categorization job scoped to that customer only.
- A guard trigger (`check_category_business_same_customer`) rejects any attempt to link a category and business that belong to different customers — this is enforced at the database level, not just in application code.

## 4. Accounting Type

Every category has an `accounting_type` — a Postgres enum with the standard chart-of-accounts classifications:

| Value | Meaning |
|---|---|
| `income` | Revenue / money coming in |
| `cogs` | Cost of goods sold — direct cost of delivering your product/service |
| `expense` | General operating expense |
| `asset` | Balance-sheet asset |
| `liability` | Balance-sheet liability |
| `equity` | Owner's equity |

This is independent of the categorizer's matching logic (tier-1/tier-2 don't look at it) — it exists so P&L and balance-sheet reporting can group transactions correctly regardless of how a category happens to be named. Every row in `seed.sql` sets this explicitly; the column defaults to `'expense'` only as a safety net for rows inserted without it.

## 5. Seed Your Data

**Edit `seed.sql` first** — the customer, business name, and category list are a starting template. Update it to match what you actually use, then:

1. SQL Editor → New query
2. Paste your edited `seed.sql`
3. Click **Run**

### Finding your Slack Team ID

`seed.sql` needs your workspace's Slack Team ID (looks like `T0123456`) to route `/run-books` commands to the right customer. Get it with:

```bash
curl -X POST https://slack.com/api/auth.test \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN"
```

The response includes `"team_id": "T0123456"`.

### Adding accounts

Add your real bank/credit accounts by uncommenting and editing the `insert into accounts` block at the bottom of `seed.sql`, or insert them directly:

```sql
insert into accounts (name, business_id, excluded)
select 'Chase Checking 1234', b.id, false
from businesses b
join customers c on c.id = b.customer_id
where c.name = 'Coding Crafts' and b.name = 'Coding Crafts';
```

### Onboarding another customer later

Copy the pattern in `seed.sql` with a new customer name and Slack Team ID, then its own businesses and categories:

```sql
insert into customers (name, slack_team_id) values ('New Client Inc', 'T9999999');

insert into businesses (customer_id, name)
select id, 'New Client Inc' from customers where name = 'New Client Inc';

-- ...categories + category_businesses for the new customer, same pattern as seed.sql
```

## 6. Get Your Connection String

1. Project Settings → Database → Connection string → **URI**
2. Use the **Session pooler** string for serverless/Railway deployments (handles connection limits better than a direct connection)
3. It looks like:
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
   ```
4. Set this as `DATABASE_URL` in `backend/.env` (local) or your Railway environment variables (production)

## Data Model Notes

- **`accounts.excluded`** replaces the old `EXCLUDED_ACCOUNT_IDS` env var. Set it directly on the account row instead of maintaining a separate ID list.
- **RLS is enabled with no policies** on every table. The backend connects via the direct Postgres URL, which bypasses RLS — tenant isolation is enforced by every application query filtering on `customer_id` (see `backend/src/clients/db_client.py`), not by RLS. RLS here only ensures the public `anon`/`authenticated` Supabase API keys can never touch this data.

## Re-running Migrations

Both `schema.sql` and `seed.sql` are idempotent — `create table if not exists`, `create index if not exists`, and `on conflict do nothing` mean you can safely re-run either file without duplicating data or erroring on existing objects.

## Inspecting Data

Supabase's **Table Editor** gives you a spreadsheet-like view of every table — useful for manually reviewing/fixing categorizations, similar to how Airtable was used before.
