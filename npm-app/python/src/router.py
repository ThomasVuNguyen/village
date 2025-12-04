"""
Routing logic for finding the best device to execute a command.
"""

from typing import Optional

from .device import get_idle_devices


def find_idle_device(id_token: str) -> Optional[str]:
    """
    Find an idle device to route command to.
    Returns device_id of first idle device, or None if none available.
    """
    idle_devices = get_idle_devices(id_token, exclude_self=True)

    if not idle_devices:
        return None

    # Sort by last_seen_at (most recent first)
    idle_devices.sort(key=lambda d: d["last_seen_at"], reverse=True)

    # Return the most recently seen idle device
    return idle_devices[0]["device_id"]
