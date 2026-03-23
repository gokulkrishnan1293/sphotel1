"""KOT (Kitchen Order Ticket) formatter. Python 3.6 compatible."""
import sys
sys.path.insert(0, ".")
from agent.fmt_helpers import bold, divider, ist


def format_kot(payload):
    tmpl = payload.get("print_template") or {}
    fs   = max(1, tmpl.get("kot_font_size", 1))
    W    = max(1, tmpl.get("kot_width", 32) // fs)

    bill_type  = payload.get("bill_type", "")
    type_label = {"table": "Dine In", "parcel": "Pick Up", "pickup": "Pick Up"}.get(
        bill_type, bill_type.replace("_", " ").title()
    )
    kot_number  = payload.get("kot_number", "")
    bill_number = payload.get("bill_number")
    printed_at  = ist(payload["printed_at"]) if payload.get("printed_at") else ""
    bkn = tmpl.get("bold_kot_number", False)
    bki = tmpl.get("bold_kot_items", False)

    lines = [""] * tmpl.get("top_padding", 2)
    lines.append(printed_at)
    if kot_number:
        lines.append(bold("KOT - {}".format(kot_number), bkn))
    if bill_number is not None:
        lines.append("Bill No.: {}".format(bill_number))
    lines.append(type_label)
    lines.append("." * W)

    item_w = max(4, W - 4)
    lines.append("{:<{}}{}".format("Item", item_w, "Qty."))
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:item_w].ljust(item_w)
        qty  = str(item.get("qty", 0)).rjust(4)
        lines.append(bold("{}{}".format(name, qty), bki))

    lines.append("." * W)
    lines += [""] * tmpl.get("bottom_padding", 5)
    return "\n".join(lines)
