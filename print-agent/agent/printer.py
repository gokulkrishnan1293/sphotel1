"""ESC/POS receipt and KOT formatter matching sphotel thermal slip format."""
from datetime import datetime

from config.agent_config import agent_settings as cfg


# ── Formatting helpers ────────────────────────────────────────────────────────

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
    rupees = paise / 100
    return f"{rupees:.2f}"


def _now_str() -> str:
    return datetime.now().strftime("%d/%m/%y %H:%M")


# ── KOT Slip format (small, no totals) ───────────────────────────────────────
#
# 28/02/26 14:44
# KOT - 46
# Pick Up
# ..........................................
# Item              Special Note      Qty.
# Parotta [1 Pc]    --                  4
# ..........................................

def format_kot(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("kot_width", cfg.RECEIPT_WIDTH)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In",
        "parcel": "Pick Up",
        "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")

    kot_number = payload.get("kot_number", "")
    printed_at = payload.get("printed_at", "")
    if printed_at:
        try:
            dt = datetime.strptime(printed_at[:16], "%Y-%m-%dT%H:%M")
            printed_at = dt.strftime("%d/%m/%y %H:%M")
        except ValueError:
            pass

    lines = []
    lines.append(printed_at)
    if kot_number:
        lines.append(f"KOT - {kot_number}")
    lines.append(type_label)
    lines.append(_dots(W))

    # Header row
    item_w = W - 20  # space for special note + qty
    header = f"{'Item':<{item_w}}{'Special Note':<12}{'Qty.':>4}"
    lines.append(header)

    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:item_w].ljust(item_w)
        note = str(item.get("special_note") or "--")[:10].ljust(12)
        qty = str(item.get("qty", 0)).rjust(4)
        lines.append(f"{name}{note}{qty}")

    lines.append(_dots(W))
    lines += ["", ""]
    return "\n".join(lines)


# ── Full Bill Receipt format ──────────────────────────────────────────────────
#
#           S.P HOTEL
#   COVAI ROAD, SHANTHI THEATRE
#        OPP, POLLACHI
#     PH : 04259 221066
#   GST NO : 33ADJS9811P1ZE
#   FSSAI : 12419003000321
# Name: ___________________________
#
# Date: 28/02/26 19:04   Pick Up
# Cashier: biller
# Token No.: 85          Bill No.: 60626
# ------------------------------------------
# Item               Qty.  Price    Amount
# ------------------------------------------
# Parotta [1 Pc]       4   25.00   100.00
# ------------------------------------------
# Total Qty: 4              Sub Total 100.00
# ------------------------------------------
#                Grand Total    100.00
# ------------------------------------------
#                    Thanks

def format_receipt(payload: dict) -> str:
    tmpl = payload.get("print_template", {})
    W = tmpl.get("receipt_width", cfg.RECEIPT_WIDTH)

    bill_type = payload.get("bill_type", "")
    type_label = {
        "table": "Dine In",
        "parcel": "Pick Up",
        "pickup": "Pick Up",
    }.get(bill_type, bill_type.replace("_", " ").title() if bill_type else "")

    printed_at = payload.get("printed_at", "")
    if printed_at:
        try:
            dt = datetime.strptime(printed_at[:16], "%Y-%m-%dT%H:%M")
            printed_at = dt.strftime("%d/%m/%y %H:%M")
        except ValueError:
            pass

    lines = []

    # ── Header ──
    if tmpl.get("restaurant_name"):
        lines.append(_center(tmpl["restaurant_name"], W))
    if tmpl.get("address_line_1"):
        lines.append(_center(tmpl["address_line_1"], W))
    if tmpl.get("address_line_2"):
        lines.append(_center(tmpl["address_line_2"], W))
    if tmpl.get("phone"):
        lines.append(_center(f"PH : {tmpl['phone']}", W))
    if tmpl.get("gst_number"):
        lines.append(_center(f"GST NO : {tmpl['gst_number']}", W))
    if tmpl.get("fssai_number"):
        lines.append(_center(f"FSSAI : {tmpl['fssai_number']}", W))

    # ── Name field ──
    if tmpl.get("show_name_field", True):
        customer = payload.get("customer_name") or ""
        lines.append(f"Name: {customer}")

    lines.append("")

    # ── Bill info ──
    date_line = f"Date: {printed_at}"
    if type_label:
        date_line = _row_left_right(date_line, type_label, W)
    lines.append(date_line)

    if tmpl.get("show_cashier", True) and payload.get("cashier"):
        lines.append(f"Cashier: {payload['cashier']}")

    token_no = payload.get("token_number")
    bill_no = payload.get("bill_number")
    token_bill_line = ""
    if tmpl.get("show_token_no", True) and token_no is not None:
        token_bill_line += f"Token No.: {token_no}"
    if tmpl.get("show_bill_no", True) and bill_no is not None:
        bill_part = f"Bill No.: {bill_no}"
        if token_bill_line:
            token_bill_line = _row_left_right(token_bill_line, bill_part, W)
        else:
            token_bill_line = bill_part
    if token_bill_line:
        lines.append(token_bill_line)

    lines.append(_divider("-", W))

    # ── Column header ──
    name_w = W - 22  # space for qty + price + amount
    col_header = f"{'Item':<{name_w}}{'Qty.':>4}  {'Price':>6}  {'Amount':>7}"
    lines.append(col_header)
    lines.append(_divider("-", W))

    # ── Line items ──
    total_qty = 0
    for item in payload.get("items", []):
        name = str(item.get("name", ""))[:name_w].ljust(name_w)
        qty = item.get("qty", 0)
        total_qty += qty
        price_paise = item.get("price_paise", 0)
        amount_paise = price_paise * qty
        price_str = _format_rupees(price_paise)
        amount_str = _format_rupees(amount_paise)
        lines.append(f"{name}{qty:>4}  {price_str:>6}  {amount_str:>7}")

    lines.append(_divider("-", W))

    # ── Totals ──
    subtotal = payload.get("subtotal_paise", 0)
    discount = payload.get("discount_paise", 0)
    total = payload.get("total_paise", 0)

    qty_label = f"Total Qty: {total_qty}"
    sub_label = f"Sub Total {_format_rupees(subtotal)}"
    lines.append(_row_left_right(qty_label, sub_label, W))

    if discount:
        lines.append(_row_left_right("", f"Discount -{_format_rupees(discount)}", W))

    lines.append(_divider("-", W))

    grand_total = f"Grand Total  {_format_rupees(total)}"
    lines.append(_center(grand_total, W))
    lines.append(_divider("-", W))

    # ── Footer ──
    footer = tmpl.get("footer_message", "Thanks")
    if footer:
        lines.append(_center(footer, W))

    lines += ["", "", ""]
    return "\n".join(lines)


# ── Dispatch & print ──────────────────────────────────────────────────────────

def print_receipt(payload: dict) -> None:
    """Format based on job_type and send to printer."""
    job_type = payload.get("job_type", "receipt")
    W = (
        payload.get("print_template", {}).get("kot_width", cfg.RECEIPT_WIDTH)
        if job_type == "kot"
        else payload.get("print_template", {}).get("receipt_width", cfg.RECEIPT_WIDTH)
    )
    text = format_kot(payload) if job_type == "kot" else format_receipt(payload)

    ptype = cfg.PRINTER_TYPE.lower()
    try:
        if ptype == "win32":
            # Use win32print directly — Win32Raw not available in escpos 2.x
            import win32print
            name = cfg.WIN32_PRINTER_NAME or win32print.GetDefaultPrinter()
            raw = text.encode("cp437", errors="replace") + b"\x1d\x56\x00"
            h = win32print.OpenPrinter(name)
            try:
                win32print.StartDocPrinter(h, 1, ("Receipt", None, "RAW"))
                win32print.StartPagePrinter(h)
                win32print.WritePrinter(h, raw)
                win32print.EndPagePrinter(h)
                win32print.EndDocPrinter(h)
            finally:
                win32print.ClosePrinter(h)
            return
        if ptype == "network":
            from escpos.printer import Network
            p = Network(cfg.PRINTER_HOST, cfg.PRINTER_PORT)
        elif ptype == "serial":
            from escpos.printer import Serial
            p = Serial(cfg.SERIAL_PORT)
        elif ptype == "file":
            from escpos.printer import File
            p = File(cfg.PRINTER_FILE)
        else:
            from escpos.printer import Usb
            p = Usb(cfg.USB_VENDOR_ID, cfg.USB_PRODUCT_ID)
        p.set(align="left", font="a", bold=False)
        p.text(text)
        p.cut()
        p.close()
    except Exception as exc:
        raise RuntimeError("Printer error ({}): {}".format(ptype, exc))
