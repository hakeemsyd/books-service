import hashlib
import hmac
import time

import httpx

from ..config import SLACK_SIGNING_SECRET, SLACK_BOT_TOKEN, SLACK_CHANNEL_ID


def verify_slack_signature(headers: dict, body: bytes) -> bool:
    timestamp = headers.get("x-slack-request-timestamp", "")
    signature = headers.get("x-slack-signature", "")
    if not timestamp or not signature:
        return False
    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False  # replay protection
    except ValueError:
        return False

    sig_basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode("utf-8"),
        sig_basestring.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(computed, signature)


async def post_message(text: str, channel: str | None = None) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={"channel": channel or SLACK_CHANNEL_ID, "text": text, "unfurl_links": False},
            timeout=30,
        )


async def post_to_response_url(response_url: str, text: str) -> None:
    async with httpx.AsyncClient() as client:
        await client.post(response_url, json={"response_type": "in_channel", "text": text}, timeout=30)
