"""Core orchestration for a single categorization run — independent of how
it's triggered (Slack slash command, CLI, future scheduled job, etc.)."""
import logging

from ..clients import (
    fetch_categories, fetch_historical_transactions,
    fetch_uncategorized_transactions, update_transactions,
)
from .categorizer import build_history_index, categorize_batch

log = logging.getLogger("books-service")


async def run_categorization(customer_id: str, dry_run: bool = False):
    """
    Fetches categories + historical + uncategorized transactions for a
    customer, categorizes the uncategorized ones, and (unless dry_run)
    persists the results.

    Returns (auto, suggested, needs_review) — same shape as categorize_batch.
    """
    log.info("Fetching category schema for customer=%s...", customer_id)
    categories_by_business, category_id_to_name = await fetch_categories(customer_id)

    log.info("Fetching historical categorized transactions...")
    historical = await fetch_historical_transactions(customer_id)
    account_name_index, name_only_index = build_history_index(historical)

    log.info("Fetching uncategorized transactions...")
    uncategorized = await fetch_uncategorized_transactions(customer_id)

    auto, suggested, needs_review = categorize_batch(
        uncategorized, account_name_index, name_only_index,
        category_id_to_name, categories_by_business,
    )

    if not dry_run:
        updates = []
        for item in auto:
            updates.append({"id": item["id"], "category_id": item["category_id"], "reviewed": True})
        for item in suggested:
            updates.append({"id": item["id"], "category_id": item["category_id"], "reviewed": False})
        if updates:
            await update_transactions(customer_id, updates)

    return auto, suggested, needs_review
