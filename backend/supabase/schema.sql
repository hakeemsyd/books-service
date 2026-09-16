-- Books Service — Supabase Postgres schema
-- Run this in Supabase → SQL Editor (or `supabase db push` if using the CLI).
-- Safe to re-run: every statement is idempotent.

create extension if not exists "pgcrypto";  -- gen_random_uuid()

-- ---------------------------------------------------------------------------
-- businesses: separate entities that share this books-service (e.g. different
-- companies whose transactions get categorized against their own category set)
-- ---------------------------------------------------------------------------
create table if not exists businesses (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    created_at timestamptz not null default now()
);

create unique index if not exists idx_businesses_name on businesses (lower(name));

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
-- categories: bookkeeping categories. A category can be shared across
-- multiple businesses via category_businesses.
-- ---------------------------------------------------------------------------
create table if not exists categories (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    created_at timestamptz not null default now()
);

create unique index if not exists idx_categories_name on categories (lower(name));

create table if not exists category_businesses (
    category_id uuid not null references categories(id) on delete cascade,
    business_id uuid not null references businesses(id) on delete cascade,
    primary key (category_id, business_id)
);

create index if not exists idx_category_businesses_business on category_businesses(business_id);

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
-- service_role key), both of which bypass RLS entirely. Enabling RLS here
-- with no policies additionally guarantees the anon/authenticated Supabase
-- API keys can never read or write this data, even by accident.
-- ---------------------------------------------------------------------------
alter table businesses enable row level security;
alter table accounts enable row level security;
alter table categories enable row level security;
alter table category_businesses enable row level security;
alter table transactions enable row level security;
