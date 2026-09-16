"""Supabase Postgres client — connection pool and queries for the books schema."""
import asyncpg

from ..config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    return _pool


async def fetch_categories():
    """
    Returns:
      categories_by_business: {business_id: {category_name_lower: category_id}}
      category_id_to_name: {category_id: category_name}
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select c.id, c.name, cb.business_id
            from categories c
            join category_businesses cb on cb.category_id = c.id
            """
        )

    categories_by_business: dict[str, dict[str, str]] = {}
    category_id_to_name: dict[str, str] = {}
    for r in rows:
        cid = str(r["id"])
        category_id_to_name[cid] = r["name"]
        categories_by_business.setdefault(str(r["business_id"]), {})[r["name"].lower()] = cid
    return categories_by_business, category_id_to_name


async def fetch_historical_transactions() -> list[dict]:
    """Categorized transactions used to build the tier-1 statistical match index."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select id, name, account_id, category_id
            from transactions
            where category_id is not null
            """
        )
    return [dict(r) for r in rows]


async def fetch_uncategorized_transactions() -> list[dict]:
    """Uncategorized transactions joined with their account's business and exclusion flag."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            select t.id, t.name, t.usd, t.date, t.account_id,
                   a.business_id, a.excluded
            from transactions t
            join accounts a on a.id = t.account_id
            where t.category_id is null
            """
        )
    return [dict(r) for r in rows]


async def update_transactions(updates: list[dict]) -> None:
    """updates: [{id, category_id, reviewed}]"""
    if not updates:
        return
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.executemany(
                """
                update transactions
                set category_id = $2, reviewed = $3, updated_at = now()
                where id = $1
                """,
                [(u["id"], u["category_id"], u["reviewed"]) for u in updates],
            )
