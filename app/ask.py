"""
Send a route (ask) from this device to another device via the portal. Uses cached/Google device-flow auth token.

Usage:
  set TO_DEVICE_ID=<target_device_id>
  set COMMAND=<cli_command_to_run_on_target>
  set ASK_URL=<override_endpoint_optional>
  python ask.py            # Send and wait for response (default)
  python ask.py --no-wait  # Send and exit immediately
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from auth import get_id_token
from firebase_config import API_KEY

DEFAULT_URL = "https://ask-wprnv4rl5q-uc.a.run.app"
ASK_URL = os.environ.get("ASK_URL", DEFAULT_URL)
RTDB_URL = "https://village-app.firebaseio.com"
DEVICE_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "device_id"
    if os.name == "nt"
    else Path.home() / ".village" / "device_id"
)


def load_device_id() -> str:
    if not DEVICE_FILE.exists():
        raise SystemExit("device_id file not found; run register_device.py first.")
    return DEVICE_FILE.read_text().strip()


def wait_for_response(route_id: str, id_token: str, timeout: int = 60) -> None:
    """Poll for response and print when received."""
    print(f"Waiting for response (timeout: {timeout}s)...", end="", flush=True)
    start_time = time.time()
    poll_interval = 1  # seconds

    while time.time() - start_time < timeout:
        try:
            resp = requests.get(
                f"{RTDB_URL}/responses/{route_id}.json?auth={id_token}",
                timeout=10,
            )
            if resp.status_code == 200 and resp.json():
                response_data = resp.json()
                output = response_data.get("output", "[no output]")
                print("\n\n" + "=" * 60)
                print("RESPONSE:")
                print("=" * 60)
                print(output)
                print("=" * 60)
                return

            print(".", end="", flush=True)
            time.sleep(poll_interval)

        except Exception as e:
            print(f"\nError checking response: {e}")
            time.sleep(poll_interval)

    print("\n[timeout] No response received")


def main() -> None:
    id_token = get_id_token()
    to_device_id = os.environ.get("TO_DEVICE_ID", "").strip()
    if not to_device_id:
        raise SystemExit("TO_DEVICE_ID env var is required.")

    from_device_id = load_device_id()
    command = os.environ.get("COMMAND", "echo hello from village")
    wait = "--no-wait" not in sys.argv  # Wait by default unless --no-wait

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

    if resp.status_code != 200:
        print(f"Error: {resp.status_code} {resp.text}")
        sys.exit(1)

    result = resp.json()
    route_id = result.get("route_id")
    print(f"Command sent: {command}")
    print(f"Route ID: {route_id}")

    if wait and route_id:
        wait_for_response(route_id, id_token)


if __name__ == "__main__":
    main()
