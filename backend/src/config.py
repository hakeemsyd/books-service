import os

# --- Airtable ---
AIRTABLE_TOKEN = os.environ["AIRTABLE_TOKEN"]          # Personal Access Token, scopes: data.records:read, data.records:write, schema.bases:read
AIRTABLE_BASE_ID = os.environ["AIRTABLE_BASE_ID"]       # e.g. applltiCCLasqIPr7
AIRTABLE_TABLE_NAME = os.environ.get("AIRTABLE_TABLE_NAME", "Transactions")
AIRTABLE_CATEGORIES_TABLE = os.environ.get("AIRTABLE_CATEGORIES_TABLE", "Categories")

# Field names as they exist in the base
FIELD_NAME = os.environ.get("FIELD_NAME", "*Name")
FIELD_USD = os.environ.get("FIELD_USD", "**USD")
FIELD_DATE = os.environ.get("FIELD_DATE", "**Date")
FIELD_ACCOUNT = os.environ.get("FIELD_ACCOUNT", "**Account")
FIELD_CATEGORY = os.environ.get("FIELD_CATEGORY", "Category")
FIELD_REVIEWED = os.environ.get("FIELD_REVIEWED", "Reviewed")
FIELD_BUSINESSES = os.environ.get("FIELD_BUSINESSES", "Businesses")  # lookup, read-only

# Accounts excluded from all processing (record IDs)
EXCLUDED_ACCOUNT_IDS = set(
    filter(None, os.environ.get(
        "EXCLUDED_ACCOUNT_IDS",
        "recSZCA8muq03PkB6,recFOW4pJVUrZpfp2"
    ).split(","))
)

# --- Slack ---
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_CHANNEL_ID = os.environ.get("SLACK_CHANNEL_ID", "")  # optional fallback channel, e.g. C0C2AEDFSGY

# --- Matching thresholds (tier 1, statistical) ---
MIN_SEEN = int(os.environ.get("MIN_SEEN", "3"))
MIN_CONSISTENCY = float(os.environ.get("MIN_CONSISTENCY", "0.9"))

# --- History pull size ---
HISTORY_PAGE_SIZE = 100
MAX_HISTORY_PAGES = int(os.environ.get("MAX_HISTORY_PAGES", "50"))  # ~5000 records cap
