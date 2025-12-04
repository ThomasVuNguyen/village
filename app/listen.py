"""
Listen for incoming commands on this device and execute them automatically.
Runs as a daemon, watching Firebase RTDB for routes targeting this device.

Usage:
  python listen.py
"""

import json
import os
import subprocess
import time
from pathlib import Path

import requests
from auth import get_id_token
from firebase_config import API_KEY

RTDB_URL = "https://village-app.firebaseio.com"
RESPOND_URL = "https://respond-wprnv4rl5q-uc.a.run.app"
DEVICE_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "device_id"
    if os.name == "nt"
    else Path.home() / ".village" / "device_id"
)


def load_device_id() -> str:
    if not DEVICE_FILE.exists():
        raise SystemExit("device_id file not found; run register_device.py first.")
    return DEVICE_FILE.read_text().strip()


def execute_command(command: str) -> str:
    """Execute command and return output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output or "[no output]"
    except subprocess.TimeoutExpired:
        return "[error] Command timed out (30s limit)"
    except Exception as e:
        return f"[error] {str(e)}"


def send_response(route_id: str, output: str, device_id: str, id_token: str) -> bool:
    """Send response back to portal."""
    try:
        resp = requests.post(
            RESPOND_URL,
            headers={"Authorization": f"Bearer {id_token}"},
            json={
                "route_id": route_id,
                "from_device_id": device_id,
                "output": output,
                "content_type": "text/plain",
            },
            timeout=15,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"Failed to send response: {e}")
        return False


def check_pending_routes(device_id: str, id_token: str, processed: set) -> None:
    """Check for pending routes targeting this device."""
    try:
        # Query routes where to_device_id matches and status is pending
        resp = requests.get(
            f"{RTDB_URL}/routes.json?auth={id_token}",
            timeout=15,
        )
        if resp.status_code != 200:
            return

        routes = resp.json()
        if not routes:
            return

        for route_id, route_data in routes.items():
            if not isinstance(route_data, dict):
                continue

            # Skip if already processed
            if route_id in processed:
                continue

            # Check if this route is for us and pending
            if (
                route_data.get("to_device_id") == device_id
                and route_data.get("status") == "pending"
            ):
                command = route_data.get("command", "")
                print(f"\n[{route_id}] Received command: {command}")

                # Execute command
                output = execute_command(command)
                print(f"[{route_id}] Output: {output[:100]}...")

                # Send response
                if send_response(route_id, output, device_id, id_token):
                    print(f"[{route_id}] Response sent successfully")
                    processed.add(route_id)
                else:
                    print(f"[{route_id}] Failed to send response")

    except Exception as e:
        print(f"Error checking routes: {e}")


def main() -> None:
    device_id = load_device_id()
    print(f"Listening for commands on device: {device_id}")
    print("Press Ctrl+C to stop\n")

    processed = set()
    poll_interval = 2  # seconds

    while True:
        try:
            id_token = get_id_token(auto_create=False)
            check_pending_routes(device_id, id_token, processed)
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\nStopping listener...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(poll_interval)


if __name__ == "__main__":
    main()
