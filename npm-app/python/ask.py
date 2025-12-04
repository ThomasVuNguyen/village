"""
Send a route (ask) from this device to another device via the portal.

Usage:
  # Mode 1: One-to-one (explicit target)
  set TO_DEVICE_ID=<target_device_id>
  set COMMAND=<cli_command_to_run_on_target>
  python ask.py            # Send and wait for response (default)
  python ask.py --no-wait  # Send and exit immediately

  # Mode 2: One-to-many (auto-route to idle device)
  set TO_DEVICE_ID=auto    # or leave empty
  set COMMAND=<cli_command_to_run_on_target>
  python ask.py
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from src.auth import get_id_token
from src.device import get_local_device_id
from src.router import find_idle_device

DEFAULT_URL = "https://ask-wprnv4rl5q-uc.a.run.app"
ASK_URL = os.environ.get("ASK_URL", DEFAULT_URL)
RTDB_URL = "https://village-app.firebaseio.com"


def wait_for_response(route_id: str, id_token: str, start_time: float, timeout: int = 240) -> None:
    """Wait for response in real-time using Firebase SSE streaming."""
    print(f"Waiting for response (timeout: {timeout}s)...", end="", flush=True)

    try:
        # Open SSE stream for this specific response path
        resp = requests.get(
            f"{RTDB_URL}/responses/{route_id}.json?auth={id_token}",
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=timeout,
        )

        if resp.status_code != 200:
            print(f"\nError: {resp.status_code} {resp.text}")
            return

        # Process SSE events
        for line in resp.iter_lines():
            # Check timeout
            if time.time() - start_time >= timeout:
                print("\n[timeout] No response received")
                return

            if not line:
                continue

            line = line.decode('utf-8')

            # Parse SSE data events
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    event_data = data.get('data')

                    # Response arrived!
                    if event_data and isinstance(event_data, dict):
                        output = event_data.get("output", "[no output]")
                        duration = time.time() - start_time
                        print("\n\n" + "=" * 60)
                        print("RESPONSE:")
                        print("=" * 60)
                        print(output)
                        print("=" * 60)
                        print(f"Time taken: {duration:.2f}s")
                        return

                except json.JSONDecodeError:
                    pass  # Ignore malformed data

            # Show progress
            if time.time() - start_time > 0.5:  # After 500ms, show dots
                print(".", end="", flush=True)

    except requests.exceptions.Timeout:
        print("\n[timeout] No response received")
    except Exception as e:
        print(f"\nError waiting for response: {e}")


def main() -> None:
    id_token = get_id_token()
    to_device_id = os.environ.get("TO_DEVICE_ID", "").strip()
    command = os.environ.get("COMMAND", "echo hello from village")
    wait = "--no-wait" not in sys.argv  # Wait by default unless --no-wait

    from_device_id = get_local_device_id()

    # Auto-routing: find idle device if TO_DEVICE_ID is "auto" or empty
    if not to_device_id or to_device_id.lower() == "auto":
        print("Auto-routing: finding idle device...")
        to_device_id = find_idle_device(id_token)
        if not to_device_id:
            print("Error: No idle devices available")
            sys.exit(1)
        print(f"Found idle device: {to_device_id}")

    start_time = time.time()
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
    print(f"Target device: {to_device_id}")
    print(f"Route ID: {route_id}")

    if wait and route_id:
        wait_for_response(route_id, id_token, start_time)


if __name__ == "__main__":
    main()
