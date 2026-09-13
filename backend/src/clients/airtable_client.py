import httpx
from urllib.parse import quote
from ..config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID

BASE_URL = "https://api.airtable.com/v0"
HEADERS = {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}


async def _get(client: httpx.AsyncClient, table: str, params: dict) -> dict:
    url = f"{BASE_URL}/{AIRTABLE_BASE_ID}/{quote(table)}"
    r = await client.get(url, headers=HEADERS, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


async def list_all_records(table: str, formula: str | None = None, fields: list[str] | None = None,
                            max_pages: int | None = None, page_size: int = 100) -> list[dict]:
    """Paginate through all records matching an optional filterByFormula."""
    records: list[dict] = []
    offset = None
    pages = 0
    async with httpx.AsyncClient() as client:
        while True:
            params: dict = {"pageSize": page_size}
            if formula:
                params["filterByFormula"] = formula
            if fields:
                params["fields[]"] = fields
            if offset:
                params["offset"] = offset
            data = await _get(client, table, params)
            records.extend(data.get("records", []))
            offset = data.get("offset")
            pages += 1
            if not offset:
                break
            if max_pages and pages >= max_pages:
                break
    return records


async def update_records(table: str, updates: list[dict]) -> None:
    """updates: [{id, fields}]. Airtable caps PATCH at 10 records per request."""
    url = f"{BASE_URL}/{AIRTABLE_BASE_ID}/{quote(table)}"
    async with httpx.AsyncClient() as client:
        for i in range(0, len(updates), 10):
            chunk = updates[i:i + 10]
            body = {"records": chunk, "typecast": True}
            r = await client.patch(url, headers=HEADERS, json=body, timeout=60)
            r.raise_for_status()
