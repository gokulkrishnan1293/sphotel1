"""
Seed script: Create the Super Admin user only.

Usage (dev):
  docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm backend \
    sh -c "PYTHONPATH=/app python /app/scripts/seed_super_admin.py"

Usage (prod — pass credentials via env):
  SEED_EMAIL=admin@example.com \
  SEED_PASSWORD=yourpassword \
  SEED_NAME=YourName \
    python /app/scripts/seed_super_admin.py

The script is idempotent — safe to run multiple times.
"""
import asyncio
import io
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.security.pin import hash_pin
from app.core.security.totp import generate_totp_secret, get_provisioning_uri

# ── Credentials (override via environment variables in prod) ──────────────────
SEED_EMAIL    = os.getenv("SEED_EMAIL",    "gokulkrishnan1293@gmail.com")
SEED_PASSWORD = os.getenv("SEED_PASSWORD", "nivedhitha@2026")
SEED_NAME     = os.getenv("SEED_NAME",     "Gokul")

PLATFORM_TENANT_ID = "platform"


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]

    async with async_session() as db:
        existing = (await db.execute(
            text("SELECT id FROM tenant_users WHERE email = :email AND role = 'super_admin'"),
            {"email": SEED_EMAIL},
        )).first()

        if existing is not None:
            print(f"ℹ️  Super admin already exists: {SEED_EMAIL}")
            return

        totp_secret = generate_totp_secret()
        await db.execute(
            text("""
                INSERT INTO tenant_users
                    (tenant_id, name, email, role, password_hash, totp_secret, is_active, preferences)
                VALUES
                    (:tenant_id, :name, :email, 'super_admin', :password_hash, :totp_secret, true, '{}')
            """),
            {
                "tenant_id": PLATFORM_TENANT_ID,
                "name": SEED_NAME,
                "email": SEED_EMAIL,
                "password_hash": hash_pin(SEED_PASSWORD),
                "totp_secret": totp_secret,
            },
        )
        await db.commit()

        totp_uri = get_provisioning_uri(totp_secret, SEED_EMAIL)
        print(f"\n✅ Super admin created!")
        print(f"   Name:  {SEED_NAME}")
        print(f"   Email: {SEED_EMAIL}")
        print(f"\n🔐 Scan this QR code with Google Authenticator / Authy:\n")
        try:
            import qrcode
            qr = qrcode.QRCode(border=1)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            buf = io.StringIO()
            qr.print_ascii(out=buf, invert=True)
            print(buf.getvalue())
        except ImportError:
            print(f"   (install qrcode package to see QR here)")
        print(f"   Secret: {totp_secret}")
        print(f"   URI:    {totp_uri}")
        print(f"\n   ⚠️  Save the TOTP secret — you cannot retrieve it later.")


if __name__ == "__main__":
    asyncio.run(seed())
