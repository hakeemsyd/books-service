"""
Run books categorization from the command line — no Slack required.

Usage (from the backend/ directory, with venv active and .env populated):

    python -m scripts.run_books --list-customers
    python -m scripts.run_books --customer "Hakeem Abbas"
    python -m scripts.run_books --customer "Hakeem Abbas" --dry-run
"""
import argparse
import asyncio
import logging
import sys

from src.clients import fetch_customer_by_name, list_customers
from src.clients.db_client import get_pool
from src.services import run_categorization, format_summary

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("books-cli")


async def _list_customers() -> None:
    customers = await list_customers()
    if not customers:
        print("No customers found. Seed one first — see backend/supabase/seed.sql.")
        return
    print(f"{'ID':<38} {'NAME':<30} SLACK_TEAM_ID")
    for c in customers:
        print(f"{str(c['id']):<38} {c['name']:<30} {c['slack_team_id'] or '-'}")


async def _run(customer_name: str, dry_run: bool) -> None:
    customer = await fetch_customer_by_name(customer_name)
    if not customer:
        print(f"No customer found named {customer_name!r}. Run with --list-customers to see what's available.")
        sys.exit(1)

    auto, suggested, needs_review = await run_categorization(customer["id"], dry_run=dry_run)
    print(format_summary(auto, suggested, needs_review))
    if dry_run:
        print("\n(dry run — no changes were written to the database)")


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Run books categorization from the command line.")
    parser.add_argument("--customer", help="Customer name to run categorization for")
    parser.add_argument("--list-customers", action="store_true", help="List all customers and exit")
    parser.add_argument("--dry-run", action="store_true", help="Compute categorization without writing to the database")
    args = parser.parse_args()

    try:
        if args.list_customers:
            await _list_customers()
        elif args.customer:
            await _run(args.customer, args.dry_run)
        else:
            parser.print_help()
            sys.exit(1)
    finally:
        pool = await get_pool()
        await pool.close()


if __name__ == "__main__":
    asyncio.run(_main())
