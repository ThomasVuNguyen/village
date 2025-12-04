"""
Listen for incoming commands on this device and execute them automatically.
Runs as a daemon, watching Firebase RTDB for routes targeting this device.

Usage:
  python listen.py
"""

import atexit
import json
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import requests
from src.auth import get_id_token
from src.device import get_local_device_id, update_device_status

RTDB_URL = "https://village-app.firebaseio.com"
RESPOND_URL = "https://respond-wprnv4rl5q-uc.a.run.app"


def execute_command(command: str) -> str:
    """Execute command and return output."""
    try:
        # Redirect stdin from /dev/null so interactive commands get EOF and exit
        # This prevents commands like llama-cli from hanging waiting for input
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=240,
            stdin=subprocess.DEVNULL,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output or "[no output]"
    except subprocess.TimeoutExpired:
        return "[error] Command timed out (240s limit)"
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


def handle_route(route_id: str, route_data: dict, device_id: str, id_token: str, processed: set) -> None:
    """Handle a single route if it's for us and pending."""
    if not isinstance(route_data, dict):
        return

    # Skip if already processed
    if route_id in processed:
        return

    # Check if this route is for us and pending
    if (
        route_data.get("to_device_id") == device_id
        and route_data.get("status") == "pending"
    ):
        command = route_data.get("command", "")
        print(f"\n[{route_id}] Received command: {command}")

        # Set status to busy
        update_device_status(device_id, "busy", id_token)

        # Execute command
        output = execute_command(command)
        print(f"[{route_id}] Output: {output[:100]}...")

        # Send response
        if send_response(route_id, output, device_id, id_token):
            print(f"[{route_id}] Response sent successfully")
            processed.add(route_id)
        else:
            print(f"[{route_id}] Failed to send response")

        # Set status back to idle
        update_device_status(device_id, "idle", id_token)


def listen_realtime(device_id: str, id_token: str, processed: set, stop_event: threading.Event) -> None:
    """Listen for routes in real-time using Firebase SSE streaming."""
    while not stop_event.is_set():
        try:
            # Open SSE stream
            resp = requests.get(
                f"{RTDB_URL}/routes.json?auth={id_token}",
                headers={"Accept": "text/event-stream"},
                stream=True,
                timeout=None,  # No timeout for streaming
            )

            if resp.status_code != 200:
                print(f"Stream error: {resp.status_code}, retrying in 5s...")
                time.sleep(5)
                continue

            # Process SSE events
            for line in resp.iter_lines():
                if stop_event.is_set():
                    break

                if not line:
                    continue

                line = line.decode('utf-8')

                # Parse SSE event
                if line.startswith('event: '):
                    event_type = line[7:].strip()
                elif line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        path = data.get('path', '')
                        event_data = data.get('data')

                        if event_data is None:
                            continue

                        # Handle different event types
                        if path == '/':
                            # Initial snapshot or full update
                            if isinstance(event_data, dict):
                                for route_id, route_data in event_data.items():
                                    # Refresh token for each command
                                    id_token = get_id_token(auto_create=False)
                                    handle_route(route_id, route_data, device_id, id_token, processed)
                        elif path.startswith('/'):
                            # Single route update
                            route_id = path[1:]  # Remove leading '/'
                            if isinstance(event_data, dict):
                                # Refresh token
                                id_token = get_id_token(auto_create=False)
                                handle_route(route_id, event_data, device_id, id_token, processed)

                    except json.JSONDecodeError:
                        pass  # Ignore malformed data
                    except Exception as e:
                        print(f"Error processing event: {e}")

        except requests.exceptions.RequestException as e:
            if not stop_event.is_set():
                print(f"Connection error: {e}, reconnecting in 5s...")
                time.sleep(5)
        except Exception as e:
            if not stop_event.is_set():
                print(f"Error: {e}, reconnecting in 5s...")
                time.sleep(5)


def main() -> None:
    device_id = get_local_device_id()
    stop_event = threading.Event()

    def cleanup(signum=None, frame=None):
        """Cleanup handler - set device offline."""
        print("\nStopping listener...")
        stop_event.set()  # Signal listener thread to stop
        try:
            # Get fresh token for cleanup
            token = get_id_token(auto_create=False)
            update_device_status(device_id, "offline", token)
            print("Device set to offline")
        except Exception as e:
            print(f"Warning: Could not update status: {e}")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)   # Ctrl+C
    signal.signal(signal.SIGTERM, cleanup)  # kill command

    # Also register atexit as fallback
    atexit.register(lambda: cleanup())

    print(f"Listening for commands on device: {device_id} (real-time mode)")
    print("Press Ctrl+C to stop\n")

    processed = set()

    # Set initial status to idle
    id_token = get_id_token(auto_create=False)
    update_device_status(device_id, "idle", id_token)

    # Start real-time listener (blocking)
    try:
        listen_realtime(device_id, id_token, processed, stop_event)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
