"""Bill receipt slip formatter."""
from agent.printer_helpers import (
    _to_ist, _center, _divider, _row_left_right, _format_rupees, cfg,
)


def _header_lines(tmpl: dict, W: int, customer_name: str = "") -> list[str]:
    lines = []
    for key, fmt in [
        ("restaurant_name", "{}"), ("address_line_1", "{}"), ("address_line_2", "{}"),
        ("phone", "PH : {}"), ("gst_number", "GST NO : {}"), ("fssai_number", "FSSAI : {}"),
    ]:
        if tmpl.get(key):
            lines.append(_center(fmt.format(tmpl[key]), W))
    if tmpl.get("show_name_field", True):
        lines.append(f"Name: {customer_name}")
    return lines


def format_receipt(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("receipt_width", cfg.RECEIPT_WIDTH)
    top_pad = tmpl.get("top_padding", 2)
    bot_pad = tmpl.get("bottom_padding", 5)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")
    printed_at = _to_ist(payload["printed_at"]) if payload.get("printed_at") else ""

    lines: list[str] = [""] * top_pad
    lines += _header_lines(tmpl, W, payload.get("customer_name") or "")
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
    lines += [_divider("-", W), f"{'Item':<{name_w}}{'Qty.':>4}  {'Price':>6}  {'Amount':>7}", _divider("-", W)]

    total_qty = 0
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:name_w].ljust(name_w)
        qty = item.get("qty", 0)
        total_qty += qty
        p = item.get("price_paise", 0)
        lines.append(f"{name}{qty:>4}  {_format_rupees(p):>6}  {_format_rupees(p * qty):>7}")

    lines.append(_divider("-", W))
    subtotal, discount, total = payload.get("subtotal_paise", 0), payload.get("discount_paise", 0), payload.get("total_paise", 0)
    lines.append(_row_left_right(f"Total Qty: {total_qty}", f"Sub Total {_format_rupees(subtotal)}", W))
    if discount:
        lines.append(_row_left_right("", f"Discount -{_format_rupees(discount)}", W))
    lines += [_divider("-", W), _center(f"Grand Total  {_format_rupees(total)}", W), _divider("-", W)]

    footer = tmpl.get("footer_message", "Thanks")
    if footer:
        lines.append(_center(footer, W))

    lines += [""] * bot_pad
    return "\n".join(lines)
