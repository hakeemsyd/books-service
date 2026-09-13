"""
Core categorization logic — a Python port of the same tiered methodology
used in the Claude-driven manual run and the daily scheduled task:

Tier 1 (statistical): match (account, normalized name) against historical
categorized transactions. Auto-write only if seen >= MIN_SEEN times at that
exact (account, name) key AND consistency >= MIN_CONSISTENCY. Reviewed = True.

Tier 2 (semantic, clear-cut only): keyword rules against the category names
that actually exist for that account's inferred business. Written but
Reviewed left False so Hakeem can do a quick confirm.

Everything else is left untouched ("needs manual categorization").
"""
import re
from collections import Counter, defaultdict

from ..config import (
    FIELD_NAME, FIELD_ACCOUNT, FIELD_CATEGORY, FIELD_USD, FIELD_DATE,
    FIELD_BUSINESSES, EXCLUDED_ACCOUNT_IDS, MIN_SEEN, MIN_CONSISTENCY
)

DIGIT_RUN = re.compile(r"\d{3,}")
NON_NAME_CHARS = re.compile(r"[^A-Z&\s]")


def normalize_name(raw: str) -> str:
    if not raw:
        return ""
    s = raw.upper()
    s = DIGIT_RUN.sub("", s)
    s = NON_NAME_CHARS.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# Tier-2 keyword rules: (regex on normalized name) -> keyword(s) to look for
# in that business's own Category *Name* text. First matching category wins.
SEMANTIC_RULES = [
    ("vendor_contractor", re.compile(r"\bVENDOR\b|\bCONTRACTOR\b|\bINVOICE\b"), ["vendor", "contractor"]),
    ("gas", re.compile(r"\bSHELL\b|\bCHEVRON\b|\bEXXON\b|\bMOBIL\b|\bCOSTCO GAS\b|\bGAS STATION\b|\bARCO\b|\bVALERO\b|\bSPEEDWAY\b|\bCIRCLE K\b"), ["gas", "fuel"]),
    ("grocery", re.compile(r"\bKROGER\b|\bSAFEWAY\b|\bTRADER JOE\b|\bWHOLE FOODS\b|\bALBERTSONS\b|\bPUBLIX\b|\bHEB\b|\bRALPHS\b"), ["grocer"]),
    ("parking_tolls", re.compile(r"\bEZPASS\b|\bEZ PASS\b|\bPARKING\b|\bTOLL\b|\bMETER\b"), ["parking", "toll"]),
    ("bank_fees", re.compile(r"\bOVERDRAFT\b|\bMAINTENANCE FEE\b|\bMONTHLY FEE\b|\bINTEREST CHARGE\b|\bNSF\b"), ["bank fee", "banking fee"]),
    ("membership", re.compile(r"\bMEMBERSHIP\b|\bCLUB DUES\b|\bANNUAL DUES\b"), ["membership", "dues", "club"]),
]

# Categories these rules must NEVER touch (too ambiguous to auto-write)
_ = re.compile(r"\bUBER\b|\bLYFT\b|\bAIRLINE|\bHOTEL\b|\bEXPEDIA\b|\bPRICELINE\b|\bTARGET\b")


def build_history_index(historical_records: list[dict]):
    """
    historical_records: raw Airtable records with fields FIELD_NAME, FIELD_ACCOUNT
    (link -> list of record ids), FIELD_CATEGORY (link -> list of record ids),
    plus we also want the linked Category's display name and its Businesses lookup
    if available as a lookup field on the transaction. If not available directly,
    pass account_business_hint separately.
    Returns:
      account_name_index: {(account_id, norm_name): Counter[category_id]}
      name_only_index: {norm_name: Counter[category_id]}
      category_names: {category_id: display_name}  (best effort, may be empty)
      account_business_votes: {account_id: Counter[business_name]}
    """
    account_name_index = defaultdict(Counter)
    name_only_index = defaultdict(Counter)
    account_business_votes = defaultdict(Counter)

    for rec in historical_records:
        f = rec.get("fields", {})
        name = f.get(FIELD_NAME, "")
        norm = normalize_name(name)
        if not norm:
            continue
        accounts = f.get(FIELD_ACCOUNT) or []
        categories = f.get(FIELD_CATEGORY) or []
        if not categories:
            continue
        cat_id = categories[0]
        account_id = accounts[0] if accounts else None

        if account_id:
            account_name_index[(account_id, norm)][cat_id] += 1
        name_only_index[norm][cat_id] += 1

        businesses = f.get(FIELD_BUSINESSES) or []
        if account_id and businesses:
            for b in businesses:
                account_business_votes[account_id][b] += 1

    return account_name_index, name_only_index, account_business_votes


def match_tier1(account_id, norm_name, account_name_index, name_only_index):
    """Returns (category_id, seen, consistency, scope) or None."""
    key = (account_id, norm_name)
    if key in account_name_index:
        counter = account_name_index[key]
        total = sum(counter.values())
        top_cat, top_count = counter.most_common(1)[0]
        consistency = top_count / total
        if total >= MIN_SEEN and consistency >= MIN_CONSISTENCY:
            return top_cat, total, consistency, "account+name"
        return None  # matched but not confident enough -> no tier1 write
    if norm_name in name_only_index:
        counter = name_only_index[norm_name]
        total = sum(counter.values())
        top_cat, top_count = counter.most_common(1)[0]
        consistency = top_count / total
        # name-only scope is intentionally never auto-written (per MIN_SEEN scope=="account+name" rule)
        return None
    return None


def match_tier2(norm_name, category_choices_for_business: dict[str, str]):
    """
    category_choices_for_business: {lowercased category display name: category_id}
    for the business this account/transaction belongs to.
    Returns category_id or None.
    """
    for _, pattern, keywords in SEMANTIC_RULES:
        if pattern.search(norm_name):
            for cat_name_lower, cat_id in category_choices_for_business.items():
                if any(kw in cat_name_lower for kw in keywords):
                    return cat_id
    return None


def categorize_batch(uncategorized_records, account_name_index, name_only_index,
                      account_business_votes, category_id_to_name, categories_by_business):
    """
    Returns three lists: auto (tier1), suggested (tier2), needs_review.
    Each item: {id, name, account, usd, date, category_id?, category_name?, tier?}
    """
    auto, suggested, needs_review = [], [], []

    for rec in uncategorized_records:
        rid = rec["id"]
        f = rec.get("fields", {})
        if f.get(FIELD_CATEGORY):
            continue  # already categorized, never touch
        accounts = f.get(FIELD_ACCOUNT) or []
        account_id = accounts[0] if accounts else None
        if account_id in EXCLUDED_ACCOUNT_IDS:
            continue
        name = f.get(FIELD_NAME, "")
        norm = normalize_name(name)
        usd = f.get(FIELD_USD)
        date = f.get(FIELD_DATE)

        item_base = {"id": rid, "name": name, "account_id": account_id, "usd": usd, "date": date}

        t1 = match_tier1(account_id, norm, account_name_index, name_only_index)
        if t1:
            cat_id, seen, consistency, scope = t1
            auto.append({**item_base, "category_id": cat_id,
                         "category_name": category_id_to_name.get(cat_id, cat_id),
                         "seen": seen, "consistency": round(consistency, 2)})
            continue

        business_name = None
        if account_id in account_business_votes and account_business_votes[account_id]:
            business_name = account_business_votes[account_id].most_common(1)[0][0]
        cat_choices = categories_by_business.get(business_name, {}) if business_name else {}
        t2 = match_tier2(norm, cat_choices)
        if t2:
            suggested.append({**item_base, "category_id": t2,
                               "category_name": category_id_to_name.get(t2, t2)})
            continue

        needs_review.append(item_base)

    return auto, suggested, needs_review
