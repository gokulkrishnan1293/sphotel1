"""KOT (Kitchen Order Ticket) slip formatter."""
from agent.printer_helpers import _to_ist, _dots, _row_left_right, cfg


def format_kot(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("kot_width", cfg.RECEIPT_WIDTH)
    top_pad = tmpl.get("top_padding", 2)
    bot_pad = tmpl.get("bottom_padding", 5)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")

    kot_number = payload.get("kot_number", "")
    bill_number = payload.get("bill_number")
    printed_at = _to_ist(payload["printed_at"]) if payload.get("printed_at") else ""

    lines: list[str] = [""] * top_pad
    lines.append(printed_at)

    if kot_number and bill_number is not None:
        lines.append(_row_left_right(f"KOT - {kot_number}", f"Bill No.: {bill_number}", W))
    elif kot_number:
        lines.append(f"KOT - {kot_number}")
    elif bill_number is not None:
        lines.append(f"Bill No.: {bill_number}")

    lines.append(type_label)
    lines.append(_dots(W))

    item_w = W - 20
    lines.append(f"{'Item':<{item_w}}{'Special Note':<12}{'Qty.':>4}")

    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:item_w].ljust(item_w)
        note = str(item.get("special_note") or "--")[:10].ljust(12)
        qty = str(item.get("qty", 0)).rjust(4)
        lines.append(f"{name}{note}{qty}")

    lines.append(_dots(W))
    lines += [""] * bot_pad
    return "\n".join(lines)
