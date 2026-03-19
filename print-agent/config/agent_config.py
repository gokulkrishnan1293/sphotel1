"""Print Agent Configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SPHOTEL_API_URL: str = "http://localhost:8000"
    AGENT_API_KEY: str = ""          # must match backend PRINT_AGENT_KEY
    PRINTER_NAME: str = ""           # label shown in backend; optional filter

    # Printer type: usb | network | serial | win32 | file
    PRINTER_TYPE: str = "usb"
    # USB printer (Epson TM-T20 defaults)
    USB_VENDOR_ID: int = 1208   # 0x04b8 Epson
    USB_PRODUCT_ID: int = 514   # 0x0202 TM-T20
    # Network/WiFi printer
    PRINTER_HOST: str = "192.168.1.100"
    PRINTER_PORT: int = 9100
    # Bluetooth (maps to COM port on Windows via Bluetooth Serial Profile)
    SERIAL_PORT: str = "COM5"
    # Windows print queue (fallback for non-ESC/POS or shared printers)
    WIN32_PRINTER_NAME: str = ""
    # File/CUPS printer path (Linux)
    PRINTER_FILE: str = "/dev/usb/lp0"

    # Local offline WS server port (127.0.0.1 only — not network accessible)
    LOCAL_WS_PORT: int = 8765

    POLL_INTERVAL_SECONDS: int = 3
    RECEIPT_WIDTH: int = 32          # chars for 58mm paper; use 42 for 80mm


agent_settings = AgentSettings()
