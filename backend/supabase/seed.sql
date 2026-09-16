-- Books Service — starter seed data
--
-- This is a STARTING POINT, not your real data. Edit the customer, business
-- name(s), and category list below to match reality, then run this in
-- Supabase → SQL Editor. Safe to re-run (idempotent upserts).
--
-- To onboard additional customers later, copy the pattern below with a new
-- customer name/slack_team_id and its own businesses/categories — categories
-- do NOT carry over between customers by design (see schema.sql).

-- ---------------------------------------------------------------------------
-- 1. Customers — one row per tenant. slack_team_id routes incoming
--    /run-books commands to the right customer (find yours with:
--    curl -X POST https://slack.com/api/auth.test \
--      -H "Authorization: Bearer $SLACK_BOT_TOKEN"
--    — see supabase/README.md).
-- ---------------------------------------------------------------------------
insert into customers (name, slack_team_id)
values
    ('Coding Crafts', 'T0123456')  -- replace T0123456 with your real Slack Team ID
on conflict (lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 2. Businesses — every business this customer tracks books for
-- ---------------------------------------------------------------------------
insert into businesses (customer_id, name)
select c.id, b.name
from customers c
cross join (values ('Coding Crafts')) as b(name)
where c.name = 'Coding Crafts'
on conflict (customer_id, lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 3. Categories — a standard small-business/consulting chart of accounts,
--    scoped to this customer. Add, remove, or rename rows to match what you
--    actually use. Every category needs an accounting_type — see the enum
--    definition in schema.sql (income, cogs, expense, asset, liability,
--    equity) — used for P&L/balance-sheet reporting, not for matching.
-- ---------------------------------------------------------------------------
insert into categories (customer_id, name, accounting_type)
select c.id, cat.name, cat.accounting_type
from customers c
cross join (values
    ('Client Income',            'income'::accounting_type),
    ('Advertising & Marketing',  'expense'::accounting_type),
    ('Bank Fees',                'expense'::accounting_type),
    ('Contractors & Vendors',    'cogs'::accounting_type),
    ('Dues & Subscriptions',     'expense'::accounting_type),
    ('Gas & Fuel',               'expense'::accounting_type),
    ('Groceries',                'expense'::accounting_type),
    ('Insurance',                'expense'::accounting_type),
    ('Meals & Entertainment',    'expense'::accounting_type),
    ('Office Supplies',          'expense'::accounting_type),
    ('Parking & Tolls',          'expense'::accounting_type),
    ('Payroll',                  'expense'::accounting_type),
    ('Professional Services',    'expense'::accounting_type),
    ('Rent',                     'expense'::accounting_type),
    ('Software & Subscriptions', 'expense'::accounting_type),
    ('Travel',                   'expense'::accounting_type),
    ('Utilities',                'expense'::accounting_type),
    ('Other',                    'expense'::accounting_type)
) as cat(name, accounting_type)
where c.name = 'Coding Crafts'
on conflict (customer_id, lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 4. Link categories to businesses. This links every category above to
--    every business under the same customer — fine when there's one
--    business, but if a customer has several businesses that should NOT
--    share the full category list, replace this with explicit per-business
--    inserts instead.
-- ---------------------------------------------------------------------------
insert into category_businesses (category_id, business_id)
select cat.id, biz.id
from categories cat
join businesses biz on biz.customer_id = cat.customer_id
join customers c on c.id = cat.customer_id
where c.name = 'Coding Crafts'
on conflict do nothing;

-- ---------------------------------------------------------------------------
-- 5. Accounts — add your real bank/credit accounts here, tied to a
--    business. Set excluded = true for accounts that should never be
--    auto-categorized (mirrors the old EXCLUDED_ACCOUNT_IDS list).
-- ---------------------------------------------------------------------------
-- insert into accounts (name, business_id, excluded)
-- select 'Chase Business Ink 5156 - old', b.id, true
-- from businesses b where b.name = 'Coding Crafts'
-- on conflict (business_id, lower(name)) do nothing;
--
-- insert into accounts (name, business_id, excluded)
-- select 'Coding Crafts Meezan', b.id, true
-- from businesses b where b.name = 'Coding Crafts'
-- on conflict (business_id, lower(name)) do nothing;
