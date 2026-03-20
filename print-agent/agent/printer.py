"""Print job dispatcher — formats and sends to the configured printer."""
from agent.printer_kot import format_kot
from agent.printer_receipt import format_receipt
from config.agent_config import agent_settings as cfg

# ESC/POS select print mode: normal vs double-size
_ESC_NORMAL = b"\x1b\x21\x00"
_ESC_DOUBLE = b"\x1b\x21\x30"


def print_receipt(payload: dict) -> None:
    """Format based on job_type and send to printer."""
    job_type = payload.get("job_type", "receipt")
    tmpl = payload.get("print_template", {})
    font_size = tmpl.get("kot_font_size" if job_type == "kot" else "receipt_font_size", 1)

    text = format_kot(payload) if job_type == "kot" else format_receipt(payload)

    ptype = cfg.PRINTER_TYPE.lower()
    try:
        if ptype == "win32":
            import win32print
            name = cfg.WIN32_PRINTER_NAME or win32print.GetDefaultPrinter()
            font_cmd = _ESC_DOUBLE if font_size >= 2 else _ESC_NORMAL
            raw = font_cmd + text.encode("cp437", errors="replace") + b"\x1d\x56\x00"
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
        p.set(align="left", font="a", bold=False, width=font_size, height=font_size)
        p.text(text)
        p.cut()
        p.close()
    except Exception as exc:
        raise RuntimeError("Printer error ({}): {}".format(ptype, exc))
