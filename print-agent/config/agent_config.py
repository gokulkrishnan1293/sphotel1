"""Print Agent Configuration — plain os.environ, compatible with Python 3.6."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path('.env'))
except ImportError:
    pass


class AgentSettings:
    SPHOTEL_API_URL   = os.environ.get('SPHOTEL_API_URL',   'http://localhost:8000')
    AGENT_API_KEY     = os.environ.get('AGENT_API_KEY',     '')
    PRINTER_NAME      = os.environ.get('PRINTER_NAME',      '')
    PRINTER_TYPE      = os.environ.get('PRINTER_TYPE',      'usb')
    USB_VENDOR_ID     = int(os.environ.get('USB_VENDOR_ID',  '1208'))
    USB_PRODUCT_ID    = int(os.environ.get('USB_PRODUCT_ID', '514'))
    PRINTER_HOST      = os.environ.get('PRINTER_HOST',      '192.168.1.100')
    PRINTER_PORT      = int(os.environ.get('PRINTER_PORT',  '9100'))
    SERIAL_PORT       = os.environ.get('SERIAL_PORT',       'COM5')
    WIN32_PRINTER_NAME = os.environ.get('WIN32_PRINTER_NAME', '')
    PRINTER_FILE      = os.environ.get('PRINTER_FILE',      '/dev/usb/lp0')
    LOCAL_WS_PORT     = int(os.environ.get('LOCAL_WS_PORT',          '8765'))
    POLL_INTERVAL_SECONDS = int(os.environ.get('POLL_INTERVAL_SECONDS', '3'))
    RECEIPT_WIDTH     = int(os.environ.get('RECEIPT_WIDTH',           '32'))


agent_settings = AgentSettings()
