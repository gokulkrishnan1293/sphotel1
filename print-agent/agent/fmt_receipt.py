"""Receipt formatter. Python 3.6 compatible."""
import sys
sys.path.insert(0, ".")
from agent.fmt_helpers import bold, center, divider, row, rs, ist


def format_receipt(payload):
    tmpl = payload.get("print_template") or {}
    # W is always the full receipt width — font scaling is height-only in the
    # printer, so the number of characters per line never changes.
    W    = max(1, tmpl.get("receipt_width", 42))
    bh   = tmpl.get("bold_header", False)
    bt   = tmpl.get("bold_total", False)

    bill_type  = payload.get("bill_type", "")
    type_label = {"table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up"}.get(
        bill_type, bill_type.replace("_", " ").title()
    )
    printed_at = ist(payload["printed_at"]) if payload.get("printed_at") else ""

    lines = [""] * tmpl.get("top_padding", 2)
    for key, fmt in [
        ("restaurant_name", "{}"), ("address_line_1", "{}"), ("address_line_2", "{}"),
        ("phone", "PH : {}"), ("gst_number", "GST NO : {}"), ("fssai_number", "FSSAI : {}"),
    ]:
        if tmpl.get(key):
            lines.append(bold(center(fmt.format(tmpl[key]), W), bh and key == "restaurant_name"))

    if tmpl.get("show_name_field", True):
        lines.append("Name: {}".format(payload.get("customer_name") or ""))
    lines.append("")
    date_line = "Date: {}".format(printed_at)
    lines.append(row(date_line, type_label, W) if type_label else date_line)
    if tmpl.get("show_cashier", True) and payload.get("cashier"):
        lines.append("Cashier: {}".format(payload["cashier"]))
    if bill_type == "table" and payload.get("waiter_name"):
        lines.append("Waiter: {}".format(payload["waiter_name"]))
    tn, bn = payload.get("token_number"), payload.get("bill_number")
    if tmpl.get("show_token_no", True) and tn is not None:
        lines.append("Token No.: {}".format(tn))
    if tmpl.get("show_bill_no", True) and bn is not None:
        lines.append("Bill No.: {}".format(bn))

    nw = max(4, W - 22)
    lines += [
        divider("-", W),
        "{:<{}}{}  {:>6}  {:>7}".format("Item", nw, "Qty.", "Price", "Amount"),
        divider("-", W),
    ]
    total_qty = 0
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:nw].ljust(nw)
        qty  = item.get("qty", 0)
        total_qty += qty
        p    = item.get("price_paise", 0)
        lines.append("{}{}  {:>6}  {:>7}".format(name, str(qty).rjust(4), rs(p), rs(p * qty)))
    lines += [divider("-", W), "Total Qty: {}".format(total_qty)]
    if payload.get("discount_paise"):
        lines.append("Discount -{}".format(rs(payload["discount_paise"])))
    lines += [
        divider("-", W),
        bold(center("Grand Total  {}".format(rs(payload.get("total_paise", 0))), W), bt),
        divider("-", W),
    ]
    footer = tmpl.get("footer_message", "Thanks")
    if footer:
        lines.append(center(footer, W))
    lines += [""] * tmpl.get("bottom_padding", 5)
    return "\n".join(lines)
