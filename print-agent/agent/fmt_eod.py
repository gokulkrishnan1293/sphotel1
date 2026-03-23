"""End-of-day report formatter. Python 3.6 compatible."""
import sys
sys.path.insert(0, ".")
from agent.fmt_helpers import bold, center, divider, row, inr


def format_eod(payload):
    tmpl    = payload.get("print_template") or {}
    summary = payload.get("summary", {})
    waiters = payload.get("waiter_rows", [])
    # W is always the full EOD width — height-only scaling, chars per line unchanged.
    W       = max(1, tmpl.get("eod_width", tmpl.get("receipt_width", 42)))
    beh     = tmpl.get("bold_eod_headers", False)

    lines = [""] * tmpl.get("top_padding", 2)
    lines.append(center("*** EOD REPORT ***", W))
    hotel = tmpl.get("restaurant_name") or "EOD Report"
    lines.append(row(hotel, summary.get("date", ""), W))
    lines.append(divider("=", W))

    lines.append(row("Total Bills",   str(summary.get("bill_count", 0)), W))
    lines.append(row("Total Revenue", inr(summary.get("total_paise", 0)), W))
    lines.append(row("Discounts",     inr(summary.get("discount_paise", 0)), W))
    lines.append(row("Voids",         str(summary.get("void_count", 0)), W))
    lines.append(divider("=", W))

    if tmpl.get("eod_show_payment", True) and summary.get("payment_breakdown"):
        lines.append(bold(center("PAYMENT SUMMARY", W), beh))
        lines.append(divider("-", W))
        pb = summary["payment_breakdown"]
        for method, amt in pb.items():
            lines.append(row(method.capitalize(), inr(amt), W))
        lines.append(divider("~", W))
        lines.append(row(
            "Total ({} bills)".format(summary.get("bill_count", 0)),
            inr(sum(pb.values())), W,
        ))
        lines.append(divider("=", W))

    if tmpl.get("eod_show_items", True) and summary.get("top_items"):
        lines.append(bold(center("ITEMS SOLD", W), beh))
        lines.append(divider("-", W))
        nw = W - 8
        for item in summary["top_items"]:
            lines.append(row(item["name"][:nw], "x{}".format(item["qty"]), W))
        lines.append(divider("=", W))

    if tmpl.get("eod_show_waiters", True) and waiters:
        lines.append(bold(center("WAITER PERFORMANCE", W), beh))
        lines.append(divider("-", W))
        for w in waiters:
            name  = w["waiter_name"][:12]
            bills = "{} bills".format(w["bill_count"])
            rev   = inr(w["revenue_paise"])
            sp1   = " " * max(1, (W - len(name) - len(bills) - len(rev)) // 2)
            sp2   = " " * max(1, W - len(name) - len(sp1) - len(bills) - len(rev))
            lines.append("{}{}{}{}{}".format(name, sp1, bills, sp2, rev))
        lines.append(divider("=", W))

    footer = tmpl.get("footer_message", "")
    if footer:
        lines.append(center(footer, W))
    lines.append(center("End of report", W))
    lines += [""] * tmpl.get("bottom_padding", 2)
    return "\n".join(lines)
