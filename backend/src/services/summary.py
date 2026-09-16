"""Human-readable summary formatting for a categorization run's results.

Shared between the Slack route (posted as a message) and the CLI runner
(printed to stdout).
"""


def fmt_amount(usd) -> str:
    if usd is None:
        return ""
    return f"${usd:,.2f}"


def fmt_list(items, limit=15) -> str:
    lines = []
    for item in items[:limit]:
        cat = f" → {item.get('category_name')}" if item.get("category_name") else ""
        lines.append(f"• {item['name']} ({fmt_amount(item['usd'])}){cat}")
    if len(items) > limit:
        lines.append(f"…and {len(items) - limit} more")
    return "\n".join(lines) if lines else "_none_"


def format_summary(auto, suggested, needs_review) -> str:
    total = len(auto) + len(suggested) + len(needs_review)
    if total == 0:
        return "✅ No new uncategorized transactions right now — books are up to date."
    parts = [f"*Manual run — books categorization*  ({total} transactions processed)"]
    parts.append(f"\n✅ *Auto-categorized* ({len(auto)})\n{fmt_list(auto)}")
    parts.append(f"\n🟡 *Suggested — please confirm in the database* ({len(suggested)})\n{fmt_list(suggested)}")
    parts.append(f"\n🔴 *Needs manual categorization* ({len(needs_review)})\n{fmt_list(needs_review)}")
    return "\n".join(parts)
