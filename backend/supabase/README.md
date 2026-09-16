# Supabase Database Setup

This directory holds the Postgres schema and seed data for the Books Service, designed to run on [Supabase](https://supabase.com).

## Files

- `schema.sql` — table definitions, indexes, triggers, RLS. Idempotent (safe to re-run).
- `seed.sql` — starter categories/business. **Edit this before running** — it's a template, not your real data.

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
| `businesses` | Each company/entity you track books for |
| `accounts` | Bank/credit accounts, each tied to one business |
| `categories` | Bookkeeping categories (shared across businesses via the junction table) |
| `category_businesses` | Which categories apply to which businesses |
| `transactions` | The actual transactions to categorize |

## 3. Seed Your Data

**Edit `seed.sql` first** — the business name and category list are a starting template based on common small-business categories. Update it to match what you actually use, then:

1. SQL Editor → New query
2. Paste your edited `seed.sql`
3. Click **Run**

Add your real accounts by uncommenting and editing the `insert into accounts` block at the bottom, or insert them directly:

```sql
insert into accounts (name, business_id, excluded)
select 'Chase Checking 1234', b.id, false
from businesses b where b.name = 'Your Business Name';
```

## 4. Get Your Connection String

1. Project Settings → Database → Connection string → **URI**
2. Use the **Session pooler** string for serverless/Railway deployments (handles connection limits better than a direct connection)
3. It looks like:
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
   ```
4. Set this as `DATABASE_URL` in `backend/.env` (local) or your Railway environment variables (production)

## Data Model Notes

- **Categories are global, businesses opt in.** A category row (e.g. "Bank Fees") exists once; `category_businesses` links it to whichever businesses use it. This avoids duplicate category rows across businesses that share categories.
- **Every account belongs to exactly one business.** The categorizer uses this to scope tier-2 keyword matching to only that business's categories — no more guessing which business an account belongs to.
- **`accounts.excluded`** replaces the old `EXCLUDED_ACCOUNT_IDS` env var. Set it directly on the account row instead of maintaining a separate ID list.
- **RLS is enabled with no policies** on every table. The backend connects via the direct Postgres URL (or `service_role` key), both of which bypass RLS — this just ensures the public `anon`/`authenticated` API keys can never touch this data.

## Re-running Migrations

Both `schema.sql` and `seed.sql` are idempotent — `create table if not exists`, `create index if not exists`, and `on conflict do nothing` mean you can safely re-run either file without duplicating data or erroring on existing objects.

## Inspecting Data

Supabase's **Table Editor** gives you a spreadsheet-like view of every table — useful for manually reviewing/fixing categorizations, similar to how Airtable was used before.
