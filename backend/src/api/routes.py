"""API route handlers."""
import logging
from urllib.parse import parse_qs

from fastapi import APIRouter, Request, BackgroundTasks, Response

from ..clients import verify_slack_signature, post_message, post_to_response_url, fetch_customer_by_slack_team
from ..services import run_categorization, format_summary

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
    team_id = form.get("team_id", [None])[0]

    customer = await fetch_customer_by_slack_team(team_id) if team_id else None
    if not customer:
        log.warning("No customer configured for Slack team_id=%s", team_id)
        return {
            "response_type": "ephemeral",
            "text": "⚠️ This Slack workspace isn't linked to a customer yet. Ask an admin to set it up.",
        }

    background_tasks.add_task(run_job, customer["id"], response_url, channel_id)

    # Slack requires an ack within 3 seconds
    return {"response_type": "ephemeral", "text": "⏳ Running books categorization now — I'll post results here shortly."}


async def run_job(customer_id: str, response_url: str | None, channel_id: str | None):
    """Runs the categorization job for a customer and posts the result to Slack."""
    try:
        auto, suggested, needs_review = await run_categorization(customer_id)
        text = format_summary(auto, suggested, needs_review)

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
