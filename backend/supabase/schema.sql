-- Books Service — Supabase Postgres schema
-- Run this in Supabase → SQL Editor (or `supabase db push` if using the CLI).
-- Safe to re-run: every statement is idempotent.

create extension if not exists "pgcrypto";  -- gen_random_uuid()

-- ---------------------------------------------------------------------------
-- customers: tenants of this service. Each customer is a distinct client —
-- typically one Slack workspace — that manages one or more businesses.
-- Every other table is scoped back to a customer, directly or transitively,
-- so one customer's data can never leak into another's.
-- ---------------------------------------------------------------------------
create table if not exists customers (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    slack_team_id text,  -- Slack workspace Team ID, e.g. "T0123456" (see supabase/README.md)
    created_at timestamptz not null default now()
);

create unique index if not exists idx_customers_name on customers (lower(name));
create unique index if not exists idx_customers_slack_team on customers (slack_team_id) where slack_team_id is not null;

-- ---------------------------------------------------------------------------
-- businesses: separate entities under a customer (e.g. different companies
-- that customer tracks books for, each with its own accounts/categories)
-- ---------------------------------------------------------------------------
create table if not exists businesses (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    name text not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_businesses_customer on businesses(customer_id);
create unique index if not exists idx_businesses_customer_name on businesses (customer_id, lower(name));

-- ---------------------------------------------------------------------------
-- accounts: bank/credit accounts (synced in from Plaid/Fintable or entered
-- manually), each tied to exactly one business
-- ---------------------------------------------------------------------------
create table if not exists accounts (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    business_id uuid not null references businesses(id) on delete cascade,
    excluded boolean not null default false,  -- true = never categorize this account's transactions
    created_at timestamptz not null default now()
);

create index if not exists idx_accounts_business on accounts(business_id);
create unique index if not exists idx_accounts_business_name on accounts (business_id, lower(name));

-- ---------------------------------------------------------------------------
-- accounting_type: the standard chart-of-accounts classification. Every
-- category is tagged with one so P&L/balance-sheet reporting can group
-- transactions correctly, independent of how a category happens to be named.
-- `create type` has no `if not exists`, so guard it with a DO block instead.
-- ---------------------------------------------------------------------------
do $$
begin
    if not exists (select 1 from pg_type where typname = 'accounting_type') then
        create type accounting_type as enum (
            'income',
            'cogs',       -- cost of goods sold
            'expense',
            'asset',
            'liability',
            'equity'
        );
    end if;
end
$$;

-- ---------------------------------------------------------------------------
-- categories: bookkeeping categories, scoped to a customer (not shared across
-- tenants). A category can still be shared across that customer's own
-- businesses via category_businesses.
-- ---------------------------------------------------------------------------
create table if not exists categories (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid not null references customers(id) on delete cascade,
    name text not null,
    accounting_type accounting_type not null default 'expense',
    created_at timestamptz not null default now()
);

alter table categories
    add column if not exists accounting_type accounting_type not null default 'expense';

create index if not exists idx_categories_customer on categories(customer_id);
create index if not exists idx_categories_accounting_type on categories(accounting_type);
create unique index if not exists idx_categories_customer_name on categories (customer_id, lower(name));

create table if not exists category_businesses (
    category_id uuid not null references categories(id) on delete cascade,
    business_id uuid not null references businesses(id) on delete cascade,
    primary key (category_id, business_id)
);

create index if not exists idx_category_businesses_business on category_businesses(business_id);

-- Guard rail: a category and business linked together must belong to the
-- same customer. Without this, a bug elsewhere could quietly link one
-- customer's category to another customer's business.
create or replace function check_category_business_same_customer()
returns trigger as $$
declare
    cat_customer uuid;
    biz_customer uuid;
begin
    select customer_id into cat_customer from categories where id = new.category_id;
    select customer_id into biz_customer from businesses where id = new.business_id;
    if cat_customer is distinct from biz_customer then
        raise exception 'category % and business % belong to different customers', new.category_id, new.business_id;
    end if;
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_category_businesses_same_customer on category_businesses;
create trigger trg_category_businesses_same_customer
    before insert or update on category_businesses
    for each row
    execute function check_category_business_same_customer();

-- ---------------------------------------------------------------------------
-- transactions: bank transactions to categorize
-- ---------------------------------------------------------------------------
create table if not exists transactions (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    usd numeric(12, 2),
    date date,
    account_id uuid not null references accounts(id) on delete cascade,
    category_id uuid references categories(id) on delete set null,
    reviewed boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_transactions_account on transactions(account_id);
create index if not exists idx_transactions_category on transactions(category_id);
-- speeds up "fetch all uncategorized" queries specifically
create index if not exists idx_transactions_uncategorized on transactions(account_id) where category_id is null;

-- keep updated_at current on every update
create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_transactions_updated_at on transactions;
create trigger trg_transactions_updated_at
    before update on transactions
    for each row
    execute function set_updated_at();

-- ---------------------------------------------------------------------------
-- Row Level Security
--
-- The backend connects with the direct Postgres connection string (or the
-- service_role key), both of which bypass RLS entirely — tenant isolation is
-- enforced in application code (every query is scoped by customer_id), not
-- by RLS. Enabling RLS here with no policies just guarantees the
-- anon/authenticated Supabase API keys can never read or write this data,
-- even by accident.
-- ---------------------------------------------------------------------------
alter table customers enable row level security;
alter table businesses enable row level security;
alter table accounts enable row level security;
alter table categories enable row level security;
alter table category_businesses enable row level security;
alter table transactions enable row level security;
