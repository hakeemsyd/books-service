-- Books Service — seed data
--
-- One customer ("Hakeem Abbas") managing five businesses of very different
-- shapes: two consulting LLCs, two rental properties, and one personal
-- finance "business". Because they're so different, categories are NOT
-- blanket cross-joined to every business (see section 4) — each business
-- gets only the category set that actually makes sense for it.
--
-- Slack is intentionally NOT wired up yet (slack_team_id is null) — this
-- customer is operated via the CLI (backend/scripts/run_books.py) for now.
-- Fill in slack_team_id later (see backend/supabase/README.md) once Slack
-- integration is turned on.
--
-- Safe to re-run (idempotent upserts).

-- ---------------------------------------------------------------------------
-- 1. Customer
-- ---------------------------------------------------------------------------
insert into customers (name, slack_team_id)
values
    ('Hakeem Abbas', null)
on conflict (lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 2. Businesses
-- ---------------------------------------------------------------------------
insert into businesses (customer_id, name)
select c.id, b.name
from customers c
cross join (values
    ('Coding Crafts LLC'),
    ('Curemed LLC'),
    ('7855 Greenridge Way'),
    ('7326 Fairytale St'),
    ('Hakeem Family Personal')
) as b(name)
where c.name = 'Hakeem Abbas'
on conflict (customer_id, lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 3. Categories — three distinct sets under this one customer:
--    (a) consulting/LLC business expenses
--    (b) rental property income/expenses
--    (c) personal finance
--    Add, remove, or rename rows to match what you actually use.
-- ---------------------------------------------------------------------------
insert into categories (customer_id, name, accounting_type)
select c.id, cat.name, cat.accounting_type
from customers c
cross join (values
    -- (a) LLC / consulting business categories
    ('Client Income',             'income'::accounting_type),
    ('Advertising & Marketing',   'expense'::accounting_type),
    ('Bank Fees',                 'expense'::accounting_type),
    ('Contractors & Vendors',     'cogs'::accounting_type),
    ('Dues & Subscriptions',      'expense'::accounting_type),
    ('Gas & Fuel',                'expense'::accounting_type),
    ('Meals & Entertainment',     'expense'::accounting_type),
    ('Office Supplies',           'expense'::accounting_type),
    ('Parking & Tolls',           'expense'::accounting_type),
    ('Payroll',                   'expense'::accounting_type),
    ('Professional Services',     'expense'::accounting_type),
    ('Software & Subscriptions',  'expense'::accounting_type),
    ('Travel',                    'expense'::accounting_type),

    -- (b) Rental property categories
    ('Rental Income',             'income'::accounting_type),
    ('Mortgage Interest',         'expense'::accounting_type),
    ('Property Tax',              'expense'::accounting_type),
    ('Property Insurance',        'expense'::accounting_type),
    ('Repairs & Maintenance',     'expense'::accounting_type),
    ('HOA / Association Fees',    'expense'::accounting_type),
    ('Property Management Fees',  'expense'::accounting_type),
    ('Depreciation',              'expense'::accounting_type),

    -- (c) Personal finance categories
    ('Personal Income',           'income'::accounting_type),
    ('Groceries',                 'expense'::accounting_type),
    ('Dining & Restaurants',      'expense'::accounting_type),
    ('Healthcare & Medical',      'expense'::accounting_type),
    ('Childcare & Education',     'expense'::accounting_type),
    ('Personal Shopping',         'expense'::accounting_type),
    ('Entertainment & Recreation','expense'::accounting_type),
    ('Auto & Transportation',     'expense'::accounting_type),
    ('Home & Household',          'expense'::accounting_type),
    ('Gifts & Donations',         'expense'::accounting_type),

    -- Shared across all businesses (catch-all)
    ('Insurance',                 'expense'::accounting_type),
    ('Utilities',                 'expense'::accounting_type),
    ('Rent',                      'expense'::accounting_type),
    ('Other',                     'expense'::accounting_type)
) as cat(name, accounting_type)
where c.name = 'Hakeem Abbas'
on conflict (customer_id, lower(name)) do nothing;

-- ---------------------------------------------------------------------------
-- 4. Link categories to businesses — targeted per business type. This is
--    deliberately NOT a blanket cross-join (unlike a single-business setup),
--    since these five businesses need very different category sets.
-- ---------------------------------------------------------------------------
insert into category_businesses (category_id, business_id)
select cat.id, biz.id
from categories cat
join customers c on c.id = cat.customer_id
join businesses biz on biz.customer_id = c.id
where c.name = 'Hakeem Abbas'
  and (
    -- Coding Crafts LLC + Curemed LLC: consulting business categories
    (biz.name in ('Coding Crafts LLC', 'Curemed LLC') and cat.name in (
        'Client Income', 'Advertising & Marketing', 'Bank Fees', 'Contractors & Vendors',
        'Dues & Subscriptions', 'Gas & Fuel', 'Meals & Entertainment', 'Office Supplies',
        'Parking & Tolls', 'Payroll', 'Professional Services', 'Software & Subscriptions',
        'Travel', 'Insurance', 'Utilities', 'Rent', 'Other'
    ))
    -- 7855 Greenridge Way + 7326 Fairytale St: rental property categories
    or (biz.name in ('7855 Greenridge Way', '7326 Fairytale St') and cat.name in (
        'Rental Income', 'Mortgage Interest', 'Property Tax', 'Property Insurance',
        'Repairs & Maintenance', 'HOA / Association Fees', 'Property Management Fees',
        'Depreciation', 'Utilities', 'Other'
    ))
    -- Hakeem Family Personal: personal finance categories
    or (biz.name = 'Hakeem Family Personal' and cat.name in (
        'Personal Income', 'Groceries', 'Dining & Restaurants', 'Healthcare & Medical',
        'Childcare & Education', 'Personal Shopping', 'Entertainment & Recreation',
        'Auto & Transportation', 'Home & Household', 'Gifts & Donations', 'Insurance',
        'Utilities', 'Rent', 'Other'
    ))
  )
on conflict do nothing;

-- ---------------------------------------------------------------------------
-- 5. Accounts — add your real bank/credit accounts here, tied to a business.
--    Set excluded = true for accounts that should never be auto-categorized.
-- ---------------------------------------------------------------------------
-- insert into accounts (name, business_id, excluded)
-- select 'Chase Business Checking', b.id, false
-- from businesses b
-- join customers c on c.id = b.customer_id
-- where c.name = 'Hakeem Abbas' and b.name = 'Coding Crafts LLC'
-- on conflict (business_id, lower(name)) do nothing;
