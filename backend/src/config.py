import os

from dotenv import load_dotenv

load_dotenv()  # loads backend/.env when present; no-op in prod where env vars are set directly

# --- Database (Supabase Postgres) ---
# Use the "Session pooler" or "Direct connection" string from
# Supabase → Project Settings → Database → Connection string (URI).
DATABASE_URL = os.environ["DATABASE_URL"]

# --- Slack (optional — only required if you're running the /slack/run-books
# HTTP endpoint; the CLI runner in scripts/run_books.py doesn't need these) ---
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")  # optional fallback channel, e.g. C0C2AEDFSGY

# --- Matching thresholds (tier 1, statistical) ---
MIN_SEEN = int(os.environ.get("MIN_SEEN", "3"))
MIN_CONSISTENCY = float(os.environ.get("MIN_CONSISTENCY", "0.9"))
