"""ESC/POS text formatters — backend renders the final print_text for every job type.

The agent receives a fully-rendered ``print_text`` string and only needs to
apply hardware-level commands (font scale, encoding, paper cut).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

_IST = timezone(timedelta(hours=5, minutes=30))


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _to_ist(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(_IST).strftime("%d/%m/%y %H:%M")
    except ValueError:
        return iso


def _center(text: str, width: int) -> str:
    return text.center(width)


def _divider(char: str = "-", width: int = 42) -> str:
    return char * width


def _dots(width: int = 42) -> str:
    return "." * width


def _row_left_right(left: str, right: str, width: int) -> str:
    gap = width - len(left) - len(right)
    return left + " " * max(1, gap) + right


def _format_rupees(paise: int) -> str:
    return f"{paise / 100:.2f}"


def _inr(paise: int) -> str:
    """Format paise as INR with thousands separator (used for EOD totals)."""
    return f"{paise / 100:,.2f}"


def _bold(text: str, enabled: bool) -> str:
    """Wrap text in bold markers when enabled. Agent converts to ESC/POS bytes."""
    return f"«B»{text}«/B»" if enabled else text


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------

def format_receipt(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("receipt_width", 42)
    top_pad = tmpl.get("top_padding", 2)
    bot_pad = tmpl.get("bottom_padding", 5)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")
    printed_at = _to_ist(payload["printed_at"]) if payload.get("printed_at") else ""

    bold_header = tmpl.get("bold_header", False)
    bold_total = tmpl.get("bold_total", False)

    lines: list[str] = [""] * top_pad

    for key, fmt in [
        ("restaurant_name", "{}"), ("address_line_1", "{}"), ("address_line_2", "{}"),
        ("phone", "PH : {}"), ("gst_number", "GST NO : {}"), ("fssai_number", "FSSAI : {}"),
    ]:
        if tmpl.get(key):
            lines.append(_bold(_center(fmt.format(tmpl[key]), W), bold_header))

    if tmpl.get("show_name_field", True):
        lines.append(f"Name: {payload.get('customer_name') or ''}")
    lines.append("")

    date_line = f"Date: {printed_at}"
    if type_label:
        date_line = _row_left_right(date_line, type_label, W)
    lines.append(date_line)

    if tmpl.get("show_cashier", True) and payload.get("cashier"):
        lines.append(f"Cashier: {payload['cashier']}")
    if bill_type == "table" and payload.get("waiter_name"):
        lines.append(f"Waiter: {payload['waiter_name']}")

    token_no, bill_no = payload.get("token_number"), payload.get("bill_number")
    token_bill = ""
    if tmpl.get("show_token_no", True) and token_no is not None:
        token_bill = f"Token No.: {token_no}"
    if tmpl.get("show_bill_no", True) and bill_no is not None:
        bp = f"Bill No.: {bill_no}"
        token_bill = _row_left_right(token_bill, bp, W) if token_bill else bp
    if token_bill:
        lines.append(token_bill)

    name_w = W - 22
    lines += [
        _divider("-", W),
        f"{'Item':<{name_w}}{'Qty.':>4}  {'Price':>6}  {'Amount':>7}",
        _divider("-", W),
    ]

    total_qty = 0
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:name_w].ljust(name_w)
        qty = item.get("qty", 0)
        total_qty += qty
        p = item.get("price_paise", 0)
        lines.append(f"{name}{qty:>4}  {_format_rupees(p):>6}  {_format_rupees(p * qty):>7}")

    lines.append(_divider("-", W))
    subtotal = payload.get("subtotal_paise", 0)
    discount = payload.get("discount_paise", 0)
    total = payload.get("total_paise", 0)
    lines.append(_row_left_right(f"Total Qty: {total_qty}", f"Sub Total {_format_rupees(subtotal)}", W))
    if discount:
        lines.append(_row_left_right("", f"Discount -{_format_rupees(discount)}", W))
    lines += [
        _divider("-", W),
        _bold(_center(f"Grand Total  {_format_rupees(total)}", W), bold_total),
        _divider("-", W),
    ]

    footer = tmpl.get("footer_message", "Thanks")
    if footer:
        lines.append(_center(footer, W))

    lines += [""] * bot_pad
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# KOT
# ---------------------------------------------------------------------------

def format_kot(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("kot_width", 32)
    top_pad = tmpl.get("top_padding", 2)
    bot_pad = tmpl.get("bottom_padding", 5)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")

    kot_number = payload.get("kot_number", "")
    bill_number = payload.get("bill_number")
    printed_at = _to_ist(payload["printed_at"]) if payload.get("printed_at") else ""

    bold_kot_number = tmpl.get("bold_kot_number", False)
    bold_kot_items = tmpl.get("bold_kot_items", False)

    lines: list[str] = [""]*top_pad
    lines.append(printed_at)

    if kot_number and bill_number is not None:
        lines.append(_bold(_row_left_right(f"KOT - {kot_number}", f"Bill No.: {bill_number}", W), bold_kot_number))
    elif kot_number:
        lines.append(_bold(f"KOT - {kot_number}", bold_kot_number))
    elif bill_number is not None:
        lines.append(_bold(f"Bill No.: {bill_number}", bold_kot_number))

    lines.append(type_label)
    lines.append(_dots(W))

    item_w = W - 20
    lines.append(f"{'Item':<{item_w}}{'Special Note':<12}{'Qty.':>4}")
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:item_w].ljust(item_w)
        note = str(item.get("special_note") or "--")[:10].ljust(12)
        qty = str(item.get("qty", 0)).rjust(4)
        lines.append(_bold(f"{name}{note}{qty}", bold_kot_items))

    lines.append(_dots(W))
    lines += [""] * bot_pad
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# EOD report
# ---------------------------------------------------------------------------

def format_eod(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    summary = payload.get("summary", {})
    waiter_rows = payload.get("waiter_rows", [])

    W = tmpl.get("receipt_width", 42)
    top_pad = tmpl.get("top_padding", 2)
    bot_pad = tmpl.get("bottom_padding", 2)

    show_payment = tmpl.get("eod_show_payment", True)
    show_items = tmpl.get("eod_show_items", True)
    show_waiters = tmpl.get("eod_show_waiters", True)
    bold_eod_headers = tmpl.get("bold_eod_headers", False)
    lines: list[str] = [""] * top_pad

    lines.append(_center("*** EOD REPORT ***", W))
    hotel_name = tmpl.get("restaurant_name") or "EOD Report"
    lines.append(_row_left_right(hotel_name, summary.get("date", ""), W))
    lines.append(_divider("=", W))

    lines.append(_row_left_right("Total Bills", str(summary.get("bill_count", 0)), W))
    lines.append(_row_left_right("Total Revenue", _inr(summary.get("total_paise", 0)), W))
    lines.append(_row_left_right("Discounts", _inr(summary.get("discount_paise", 0)), W))
    lines.append(_row_left_right("Voids", str(summary.get("void_count", 0)), W))
    lines.append(_divider("=", W))

    if show_payment and summary.get("payment_breakdown"):
        lines.append(_bold(_center("PAYMENT SUMMARY", W), bold_eod_headers))
        lines.append(_divider("-", W))
        pb = summary["payment_breakdown"]
        for method, amt in pb.items():
            lines.append(_row_left_right(method.capitalize(), _inr(amt), W))
        lines.append(_divider("~", W))
        total_revenue = sum(pb.values())
        lines.append(_row_left_right(
            f"Total ({summary.get('bill_count', 0)} bills)", _inr(total_revenue), W
        ))
        lines.append(_divider("=", W))

    if show_items and summary.get("top_items"):
        lines.append(_bold(_center("ITEMS SOLD", W), bold_eod_headers))
        lines.append(_divider("-", W))
        name_w = W - 8
        for item in summary["top_items"]:
            lines.append(_row_left_right(item["name"][:name_w], f"x{item['qty']}", W))
        lines.append(_divider("=", W))

    if show_waiters and waiter_rows:
        lines.append(_bold(_center("WAITER PERFORMANCE", W), bold_eod_headers))
        lines.append(_divider("-", W))
        for w in waiter_rows:
            name = w["waiter_name"][:12]
            bills = f"{w['bill_count']} bills"
            rev = _inr(w["revenue_paise"])
            space1 = " " * max(1, (W - len(name) - len(bills) - len(rev)) // 2)
            space2 = " " * max(1, W - len(name) - len(space1) - len(bills) - len(rev))
            lines.append(f"{name}{space1}{bills}{space2}{rev}")
        lines.append(_divider("=", W))

    footer = tmpl.get("footer_message", "")
    if footer:
        lines.append(_center(footer, W))
    lines.append(_center("End of report", W))

    lines += [""] * bot_pad
    return "\n".join(lines)
