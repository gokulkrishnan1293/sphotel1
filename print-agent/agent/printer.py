from config.agent_config import agent_settings as cfg

# ESC/POS print mode: normal vs double-height only
# 0x00 = Font A, 1x width, 1x height (normal)
# 0x10 = Font A, 1x width, 2x height only
#        -> text is taller/easier to read, same width -> alignment preserved, crisp
_ESC_NORMAL       = b"\x1b\x21\x00"
_ESC_TALL         = b"\x1b\x21\x10"

# ESC/POS bold on/off
_BOLD_ON  = b"\x1b\x45\x01"
_BOLD_OFF = b"\x1b\x45\x00"

# Bold markers embedded by the backend formatter («B»...«/B»)
_BSTART  = "\u00abB\u00bb"    # «B»
_BEND    = "\u00ab/B\u00bb"   # «/B»
# Double-height markers («DH»...«/DH»)
_DHSTART = "\u00abDH\u00bb"   # «DH»
_DHEND   = "\u00ab/DH\u00bb"  # «/DH»


def _parse_segments(text):
    """Split text into (segment_text, is_bold, is_tall) tuples."""
    result = []

    def _split_bold(seg, is_tall):
        parts = seg.split(_BSTART)
        if parts[0]:
            result.append((parts[0], False, is_tall))
        for part in parts[1:]:
            sub = part.split(_BEND, 1)
            result.append((sub[0], True, is_tall))
            if len(sub) > 1 and sub[1]:
                result.append((sub[1], False, is_tall))

    dh_parts = text.split(_DHSTART)
    _split_bold(dh_parts[0], False)
    for part in dh_parts[1:]:
        sub = part.split(_DHEND, 1)
        _split_bold(sub[0], True)
        if len(sub) > 1 and sub[1]:
            _split_bold(sub[1], False)

    return result


def _to_raw_bytes(text, base_font_cmd, encoding="cp437"):
    """Encode print_text (with bold/double-height markers) into ESC/POS raw bytes."""
    raw = base_font_cmd
    for seg, is_bold, is_tall in _parse_segments(text):
        if is_tall:
            raw += _ESC_TALL
        if is_bold:
            raw += _BOLD_ON
        raw += seg.encode(encoding, errors="replace")
        if is_bold:
            raw += _BOLD_OFF
        if is_tall:
            raw += base_font_cmd  # restore base font after tall segment
    return raw


def print_receipt(payload):
    """Send a pre-rendered print job to the configured printer."""
    text = payload.get("print_text", "")
    font_size = payload.get("font_size", 1)

    ptype = cfg.PRINTER_TYPE.lower()
    try:
        if ptype == "win32":
            import win32print
            name = cfg.WIN32_PRINTER_NAME or win32print.GetDefaultPrinter()
            font_cmd = _ESC_TALL if font_size >= 2 else _ESC_NORMAL
            raw = _to_raw_bytes(text, font_cmd) + b"\x1d\x56\x00"
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
        for seg, is_bold, is_tall in _parse_segments(text):
            # height=2 for double-height segments or when whole job is font_size>=2
            h = 2 if (is_tall or font_size >= 2) else 1
            p.set(align="left", font="a", bold=is_bold, width=1, height=h)
            p.text(seg)
        p.cut()
        p.close()
    except Exception as exc:
        raise RuntimeError("Printer error ({}): {}".format(ptype, exc))


