-- Books Service — starter seed data
--
-- This is a STARTING POINT, not your real chart of accounts. Edit the
-- business name(s) and category list below to match what you actually use,
-- then run this in Supabase → SQL Editor. Safe to re-run (idempotent upserts).

-- ---------------------------------------------------------------------------
-- 1. Businesses — one row per company/entity whose books you track
-- ---------------------------------------------------------------------------
insert into businesses (name)
values
    ('Coding Crafts')
on conflict (lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 2. Categories — a standard small-business/consulting chart of accounts.
--    Add, remove, or rename rows to match your Airtable "Categories" list.
-- ---------------------------------------------------------------------------
insert into categories (name)
values
    ('Advertising & Marketing'),
    ('Bank Fees'),
    ('Contractors & Vendors'),
    ('Dues & Subscriptions'),
    ('Gas & Fuel'),
    ('Groceries'),
    ('Insurance'),
    ('Meals & Entertainment'),
    ('Office Supplies'),
    ('Parking & Tolls'),
    ('Payroll'),
    ('Professional Services'),
    ('Rent'),
    ('Software & Subscriptions'),
    ('Travel'),
    ('Utilities'),
    ('Other')
on conflict (lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 3. Link every category above to "Coding Crafts". If you add more
--    businesses, give each its own explicit list here — don't assume every
--    business uses every category.
-- ---------------------------------------------------------------------------
insert into category_businesses (category_id, business_id)
select c.id, b.id
from categories c
cross join businesses b
where b.name = 'Coding Crafts'
on conflict do nothing;

-- ---------------------------------------------------------------------------
-- 4. Accounts — add your real bank/credit accounts here, tied to the business
--    above. Set excluded = true for accounts that should never be
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
