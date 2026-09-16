"""API route handlers."""
import logging
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, BackgroundTasks, Response

from ..clients import (
    verify_slack_signature, post_message, post_to_response_url,
    fetch_categories, fetch_historical_transactions, fetch_uncategorized_transactions,
    update_transactions,
)
from ..services import build_history_index, categorize_batch

log = logging.getLogger("books-service")
router = APIRouter()


@router.get("/")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@router.post("/slack/run-books")
async def run_books_command(request: Request, background_tasks: BackgroundTasks):
    """Slack command handler for running books categorization."""
    body = await request.body()
    if not verify_slack_signature(request.headers, body):
        return Response(status_code=401, content="invalid signature")

    form = parse_qs(body.decode("utf-8"))
    response_url = form.get("response_url", [None])[0]
    channel_id = form.get("channel_id", [None])[0]

    background_tasks.add_task(run_job, response_url, channel_id)

    # Slack requires an ack within 3 seconds
    return {"response_type": "ephemeral", "text": "⏳ Running books categorization now — I'll post results here shortly."}


async def run_job(response_url: str | None, channel_id: str | None):
    """Main job to categorize uncategorized transactions."""
    try:
        log.info("Fetching category schema...")
        categories_by_business, category_id_to_name = await fetch_categories()

        log.info("Fetching historical categorized transactions...")
        historical = await fetch_historical_transactions()
        account_name_index, name_only_index = build_history_index(historical)

        log.info("Fetching uncategorized transactions...")
        uncategorized = await fetch_uncategorized_transactions()

        auto, suggested, needs_review = categorize_batch(
            uncategorized, account_name_index, name_only_index,
            category_id_to_name, categories_by_business,
        )

        updates = []
        for item in auto:
            updates.append({"id": item["id"], "category_id": item["category_id"], "reviewed": True})
        for item in suggested:
            updates.append({"id": item["id"], "category_id": item["category_id"], "reviewed": False})

        if updates:
            await update_transactions(updates)

        text = _format_summary(auto, suggested, needs_review)

        if response_url:
            await post_to_response_url(response_url, text)
        else:
            await post_message(text, channel=channel_id)

    except Exception as e:
        log.exception("run_job failed")
        err_text = f"⚠️ Books categorization run failed: `{e}`"
        if response_url:
            await post_to_response_url(response_url, err_text)
        else:
            await post_message(err_text, channel=channel_id)


def _fmt_amount(usd):
    """Format USD amount."""
    if usd is None:
        return ""
    return f"${usd:,.2f}"


def _fmt_list(items, limit=15):
    """Format items as a list with optional limit."""
    lines = []
    for item in items[:limit]:
        cat = f" → {item.get('category_name')}" if item.get("category_name") else ""
        lines.append(f"• {item['name']} ({_fmt_amount(item['usd'])}){cat}")
    if len(items) > limit:
        lines.append(f"…and {len(items) - limit} more")
    return "\n".join(lines) if lines else "_none_"


def _format_summary(auto, suggested, needs_review) -> str:
    """Format categorization results as Slack message."""
    total = len(auto) + len(suggested) + len(needs_review)
    if total == 0:
        return "✅ No new uncategorized transactions right now — books are up to date."
    parts = [f"*Manual run — books categorization*  ({total} transactions processed)"]
    parts.append(f"\n✅ *Auto-categorized* ({len(auto)})\n{_fmt_list(auto)}")
    parts.append(f"\n🟡 *Suggested — please confirm in the database* ({len(suggested)})\n{_fmt_list(suggested)}")
    parts.append(f"\n🔴 *Needs manual categorization* ({len(needs_review)})\n{_fmt_list(needs_review)}")
    return "\n".join(parts)
