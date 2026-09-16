"""
Core categorization logic — a tiered methodology:

Tier 1 (statistical): match (account, normalized name) against historical
categorized transactions. Auto-write only if seen >= MIN_SEEN times at that
exact (account, name) key AND consistency >= MIN_CONSISTENCY. Reviewed = True.

Tier 2 (semantic, clear-cut only): keyword rules against the category names
that exist for the transaction's business. Written but Reviewed left False
so a human can do a quick confirm.

Everything else is left untouched ("needs manual categorization").
"""
import re
from collections import Counter, defaultdict

from ..config import MIN_SEEN, MIN_CONSISTENCY

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
# in that business's own category names. First matching category wins.
SEMANTIC_RULES = [
    ("vendor_contractor", re.compile(r"\bVENDOR\b|\bCONTRACTOR\b|\bINVOICE\b"), ["vendor", "contractor"]),
    ("gas", re.compile(r"\bSHELL\b|\bCHEVRON\b|\bEXXON\b|\bMOBIL\b|\bCOSTCO GAS\b|\bGAS STATION\b|\bARCO\b|\bVALERO\b|\bSPEEDWAY\b|\bCIRCLE K\b"), ["gas", "fuel"]),
    ("grocery", re.compile(r"\bKROGER\b|\bSAFEWAY\b|\bTRADER JOE\b|\bWHOLE FOODS\b|\bALBERTSONS\b|\bPUBLIX\b|\bHEB\b|\bRALPHS\b"), ["grocer"]),
    ("parking_tolls", re.compile(r"\bEZPASS\b|\bEZ PASS\b|\bPARKING\b|\bTOLL\b|\bMETER\b"), ["parking", "toll"]),
    ("bank_fees", re.compile(r"\bOVERDRAFT\b|\bMAINTENANCE FEE\b|\bMONTHLY FEE\b|\bINTEREST CHARGE\b|\bNSF\b"), ["bank fee", "banking fee"]),
    ("membership", re.compile(r"\bMEMBERSHIP\b|\bCLUB DUES\b|\bANNUAL DUES\b"), ["membership", "dues", "club"]),
]


def build_history_index(historical_records: list[dict]):
    """
    historical_records: [{id, name, account_id, category_id}] for transactions
    that already have a category set.

    Returns:
      account_name_index: {(account_id, norm_name): Counter[category_id]}
      name_only_index: {norm_name: Counter[category_id]}
    """
    account_name_index = defaultdict(Counter)
    name_only_index = defaultdict(Counter)

    for rec in historical_records:
        norm = normalize_name(rec.get("name", ""))
        if not norm:
            continue
        category_id = rec.get("category_id")
        if not category_id:
            continue
        account_id = rec.get("account_id")

        if account_id:
            account_name_index[(account_id, norm)][category_id] += 1
        name_only_index[norm][category_id] += 1

    return account_name_index, name_only_index


def match_tier1(account_id, norm_name, account_name_index, name_only_index):
    """Returns (category_id, seen, consistency) or None."""
    key = (account_id, norm_name)
    if key in account_name_index:
        counter = account_name_index[key]
        total = sum(counter.values())
        top_cat, top_count = counter.most_common(1)[0]
        consistency = top_count / total
        if total >= MIN_SEEN and consistency >= MIN_CONSISTENCY:
            return top_cat, total, consistency
        return None  # matched but not confident enough -> no tier1 write
    if norm_name in name_only_index:
        # name-only scope is intentionally never auto-written
        return None
    return None


def match_tier2(norm_name, category_choices_for_business: dict[str, str]):
    """
    category_choices_for_business: {lowercased category name: category_id}
    for the transaction's business.
    Returns category_id or None.
    """
    for _, pattern, keywords in SEMANTIC_RULES:
        if pattern.search(norm_name):
            for cat_name_lower, cat_id in category_choices_for_business.items():
                if any(kw in cat_name_lower for kw in keywords):
                    return cat_id
    return None


def categorize_batch(uncategorized_records, account_name_index, name_only_index,
                      category_id_to_name, categories_by_business):
    """
    uncategorized_records: [{id, name, usd, date, account_id, business_id, excluded}]
    categories_by_business: {business_id: {category_name_lower: category_id}}

    Returns three lists: auto (tier1), suggested (tier2), needs_review.
    Each item: {id, name, account_id, usd, date, category_id?, category_name?, ...}
    """
    auto, suggested, needs_review = [], [], []

    for rec in uncategorized_records:
        if rec.get("excluded"):
            continue

        account_id = rec.get("account_id")
        name = rec.get("name", "")
        norm = normalize_name(name)

        item_base = {
            "id": rec["id"], "name": name, "account_id": account_id,
            "usd": rec.get("usd"), "date": rec.get("date"),
        }

        t1 = match_tier1(account_id, norm, account_name_index, name_only_index)
        if t1:
            cat_id, seen, consistency = t1
            auto.append({**item_base, "category_id": cat_id,
                         "category_name": category_id_to_name.get(cat_id, cat_id),
                         "seen": seen, "consistency": round(consistency, 2)})
            continue

        cat_choices = categories_by_business.get(str(rec.get("business_id")), {})
        t2 = match_tier2(norm, cat_choices)
        if t2:
            suggested.append({**item_base, "category_id": t2,
                               "category_name": category_id_to_name.get(t2, t2)})
            continue

        needs_review.append(item_base)

    return auto, suggested, needs_review
