"""
Device management utilities for querying and managing devices.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

import requests

RTDB_URL = "https://village-app.firebaseio.com"
DEVICE_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "device_id"
    if os.name == "nt"
    else Path.home() / ".village" / "device_id"
)


def get_local_device_id() -> str:
    """Get the device_id for this machine."""
    if not DEVICE_FILE.exists():
        raise SystemExit("device_id file not found; run register_device.py first.")
    return DEVICE_FILE.read_text().strip()


def get_all_user_devices(id_token: str) -> Dict[str, dict]:
    """Get all devices registered to the current user."""
    try:
        resp = requests.get(
            f"{RTDB_URL}/devices.json?auth={id_token}",
            timeout=15,
        )
        if resp.status_code != 200:
            return {}

        devices = resp.json()
        if not devices:
            return {}

        return devices
    except Exception as e:
        print(f"Error fetching devices: {e}")
        return {}


def get_idle_devices(id_token: str, exclude_self: bool = True) -> List[Dict[str, str]]:
    """Get all devices with status='idle'."""
    devices = get_all_user_devices(id_token)
    local_device_id = get_local_device_id() if exclude_self else None

    idle_devices = []
    for device_id, device_data in devices.items():
        if not isinstance(device_data, dict):
            continue

        # Skip self if requested
        if exclude_self and device_id == local_device_id:
            continue

        # Check if idle
        if device_data.get("status") == "idle":
            idle_devices.append({
                "device_id": device_id,
                "name": device_data.get("name", device_id),
                "last_seen_at": device_data.get("last_seen_at", 0),
            })

    return idle_devices


def update_device_status(device_id: str, status: str, id_token: str) -> bool:
    """Update device status (idle/busy)."""
    try:
        import time
        resp = requests.patch(
            f"{RTDB_URL}/devices/{device_id}.json?auth={id_token}",
            json={
                "status": status,
                "last_seen_at": int(time.time()),
            },
            timeout=10,
        )
        return resp.status_code == 200
    except Exception as e:
        print(f"Error updating device status: {e}")
        return False
