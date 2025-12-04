"""
Remove cached auth token (but keeps device_id permanent).

Usage:
  python sign_out.py          # clears auth only
  python sign_out.py --reset  # clears auth AND device_id
"""

import os
import sys
from pathlib import Path


def main() -> None:
    base = (
        Path(os.environ["APPDATA"]) / "village"
        if os.name == "nt"
        else Path.home() / ".village"
    )
    auth_file = base / "auth.json"
    device_file = base / "device_id"

    # Check if --reset flag is provided
    reset_device = "--reset" in sys.argv

    removed_any = False

    # Always remove auth token
    if auth_file.exists():
        auth_file.unlink()
        print(f"Removed {auth_file}")
        removed_any = True

    # Only remove device_id if --reset flag is provided
    if reset_device:
        if device_file.exists():
            device_file.unlink()
            print(f"Removed {device_file}")
            removed_any = True
    else:
        if device_file.exists():
            print(f"Kept device_id: {device_file.read_text().strip()}")

    if not removed_any:
        print("No cached auth files found.")


if __name__ == "__main__":
    main()
