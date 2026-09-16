"""Supabase Postgres client — connection pool and queries for the books schema.

Every query below is scoped to a single customer_id. There is no query in
this module that reads or writes across customers — that boundary is what
keeps tenants isolated, since the backend connects with a privileged
connection string that bypasses Postgres RLS.
"""
import asyncpg

from ..config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def fetch_customer_by_slack_team(slack_team_id: str) -> dict | None:
    """Look up which customer a Slack workspace belongs to."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "select id, name from customers where slack_team_id = $1",
            slack_team_id,
        )
    return dict(row) if row else None


async def fetch_categories(customer_id: str):
    """
    Returns:
      categories_by_business: {business_id: {category_name_lower: category_id}}
      category_id_to_name: {category_id: category_name}
    Scoped to the given customer via categories.customer_id.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select c.id, c.name, cb.business_id
            from categories c
            join category_businesses cb on cb.category_id = c.id
            where c.customer_id = $1
            """,
            customer_id,
        )

    categories_by_business: dict[str, dict[str, str]] = {}
    category_id_to_name: dict[str, str] = {}
    for r in rows:
        cid = str(r["id"])
        category_id_to_name[cid] = r["name"]
        categories_by_business.setdefault(str(r["business_id"]), {})[r["name"].lower()] = cid
    return categories_by_business, category_id_to_name


async def fetch_historical_transactions(customer_id: str) -> list[dict]:
    """Categorized transactions used to build the tier-1 statistical match index."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select t.id, t.name, t.account_id, t.category_id
            from transactions t
            join accounts a on a.id = t.account_id
            join businesses b on b.id = a.business_id
            where t.category_id is not null
              and b.customer_id = $1
            """,
            customer_id,
        )
    return [dict(r) for r in rows]


async def fetch_uncategorized_transactions(customer_id: str) -> list[dict]:
    """Uncategorized transactions joined with their account's business and exclusion flag."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select t.id, t.name, t.usd, t.date, t.account_id,
                   a.business_id, a.excluded
            from transactions t
            join accounts a on a.id = t.account_id
            join businesses b on b.id = a.business_id
            where t.category_id is null
              and b.customer_id = $1
            """,
            customer_id,
        )
    return [dict(r) for r in rows]


async def update_transactions(customer_id: str, updates: list[dict]) -> None:
    """
    updates: [{id, category_id, reviewed}]

    The customer_id join in the WHERE clause is a defense-in-depth check —
    it silently no-ops any row whose transaction doesn't actually belong to
    this customer, rather than trusting the caller never to mix up ids.
    """
    if not updates:
        return
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(
                """
                update transactions t
                set category_id = $2, reviewed = $3, updated_at = now()
                from accounts a, businesses b
                where t.id = $1
                  and a.id = t.account_id
                  and b.id = a.business_id
                  and b.customer_id = $4
                """,
                [(u["id"], u["category_id"], u["reviewed"], customer_id) for u in updates],
            )
