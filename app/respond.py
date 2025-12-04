"""
Send a response for a given route. Uses cached/Google device-flow auth token.

Usage:
  set ROUTE_ID=<route_id_from_ask>
  set OUTPUT=<response_output_text>
  set RESPOND_URL=<override_endpoint_optional>
  python respond.py
"""

import json
import os
from pathlib import Path

import requests
from auth import get_id_token

DEFAULT_URL = "https://respond-wprnv4rl5q-uc.a.run.app"
RESPOND_URL = os.environ.get("RESPOND_URL", DEFAULT_URL)
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
    route_id = os.environ.get("ROUTE_ID", "").strip()
    if not route_id:
        raise SystemExit("ROUTE_ID env var is required.")

    from_device_id = load_device_id()
    output = os.environ.get("OUTPUT", "ok")

    resp = requests.post(
        RESPOND_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={
            "route_id": route_id,
            "from_device_id": from_device_id,
            "output": output,
            "content_type": "text/plain",
        },
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
