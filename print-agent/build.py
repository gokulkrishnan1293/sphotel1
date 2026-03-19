"""PyInstaller build script — produces launcher.exe (service) + agent.exe (updatable)."""
import subprocess
import sys


def build() -> None:
    print("Building agent.exe ...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "agent",
        "--add-data", "config;config",
        "--hidden-import", "escpos",
        "--hidden-import", "websockets",
        "--hidden-import", "passlib.handlers.bcrypt",
        "agent/main.py",
    ])

    print("\nBuilding launcher.exe ...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "launcher",
        "--add-data", "config;config",
        "--hidden-import", "requests",
        "launcher/launcher.py",
    ])

    print("\nBuild complete — output in dist/")
    print("  dist/launcher.exe  — install as Windows Service (never updated)")
    print("  dist/agent.exe     — upload to S3/R2 for auto-update delivery")


if __name__ == "__main__":
    build()
