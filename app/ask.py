"""
Send a route (ask) from this device to another device via the portal. Uses cached/Google device-flow auth token.

Usage:
  set TO_DEVICE_ID=<target_device_id>
  set COMMAND=<cli_command_to_run_on_target>
  set ASK_URL=<override_endpoint_optional>
  python ask.py
"""

import json
import os
from pathlib import Path

import requests
from auth import get_id_token

DEFAULT_URL = "https://ask-wprnv4rl5q-uc.a.run.app"
ASK_URL = os.environ.get("ASK_URL", DEFAULT_URL)
DEVICE_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "device_id"
    if os.name == "nt"
    else Path.home() / ".village" / "device_id"
)


def load_device_id() -> str:
    if not DEVICE_FILE.exists():
        raise SystemExit("device_id file not found; run register_device.py first.")
    return DEVICE_FILE.read_text().strip()


def main() -> None:
    id_token = get_id_token()
    to_device_id = os.environ.get("TO_DEVICE_ID", "").strip()
    if not to_device_id:
        raise SystemExit("TO_DEVICE_ID env var is required.")

    from_device_id = load_device_id()
    command = os.environ.get("COMMAND", "echo hello from village")

    resp = requests.post(
        ASK_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={
            "from_device_id": from_device_id,
            "to_device_id": to_device_id,
            "command": command,
            "content_type": "text/plain",
        },
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
