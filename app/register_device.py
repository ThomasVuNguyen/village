"""
Register the local device with the portal. Uses cached/Google device-flow auth token.

Usage:
  python register_device.py [optional-name]

Creates/reads a persistent device_id at ~/.village/device_id (or %APPDATA%\village\device_id on Windows),
then calls the register_device HTTPS endpoint.
"""

import os
import sys
import uuid
from pathlib import Path

import requests
from auth import get_id_token

REGISTER_URL = "https://register-device-wprnv4rl5q-uc.a.run.app"
DEVICE_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "device_id"
    if os.name == "nt"
    else Path.home() / ".village" / "device_id"
)


def load_or_create_device_id() -> str:
    if DEVICE_FILE.exists():
        return DEVICE_FILE.read_text().strip()
    DEVICE_FILE.parent.mkdir(parents=True, exist_ok=True)
    device_id = str(uuid.uuid4())
    DEVICE_FILE.write_text(device_id)
    return device_id


def main() -> None:
    id_token = get_id_token()

    device_id = load_or_create_device_id()
    name = " ".join(sys.argv[1:]).strip() or device_id

    resp = requests.post(
        REGISTER_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={"device_id": device_id, "name": name},
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
