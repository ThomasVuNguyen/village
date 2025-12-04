"""
Show all registered devices and their status.

Usage:
  python status.py
"""

from src.auth import get_id_token
from src.device import get_all_user_devices, get_local_device_id


def format_time_ago(timestamp: int) -> str:
    """Format timestamp as 'X minutes/hours/days ago'."""
    import time

    now = int(time.time())
    diff = now - timestamp

    if diff < 60:
        return "just now"
    elif diff < 3600:
        mins = diff // 60
        return f"{mins}m ago"
    elif diff < 86400:
        hours = diff // 3600
        return f"{hours}h ago"
    else:
        days = diff // 86400
        return f"{days}d ago"


def main() -> None:
    id_token = get_id_token(auto_create=False)
    devices = get_all_user_devices(id_token)

    if not devices:
        print("No devices registered yet.")
        print("\nRun 'village register' to register this device.")
        return

    try:
        local_device_id = get_local_device_id()
    except SystemExit:
        local_device_id = None

    print("=" * 80)
    print("YOUR DEVICES")
    print("=" * 80)

    # Group by status
    idle_devices = []
    busy_devices = []
    offline_devices = []

    for device_id, device_data in devices.items():
        status = device_data.get("status", "unknown")
        if status == "idle":
            idle_devices.append((device_id, device_data))
        elif status == "busy":
            busy_devices.append((device_id, device_data))
        else:
            offline_devices.append((device_id, device_data))

    # Print idle devices
    if idle_devices:
        print("\n💚 IDLE (available for commands)")
        print("-" * 80)
        for device_id, device_data in idle_devices:
            is_current = device_id == local_device_id
            marker = " (this device)" if is_current else ""
            name = device_data.get("name", device_id)
            last_seen = format_time_ago(device_data.get("last_seen_at", 0))
            print(f"  {name}{marker}")
            print(f"    ID: {device_id}")
            print(f"    Last seen: {last_seen}")
            print()

    # Print busy devices
    if busy_devices:
        print("\n🔴 BUSY (executing command)")
        print("-" * 80)
        for device_id, device_data in busy_devices:
            is_current = device_id == local_device_id
            marker = " (this device)" if is_current else ""
            name = device_data.get("name", device_id)
            last_seen = format_time_ago(device_data.get("last_seen_at", 0))
            print(f"  {name}{marker}")
            print(f"    ID: {device_id}")
            print(f"    Last seen: {last_seen}")
            print()

    # Print offline devices
    if offline_devices:
        print("\n⚪ OFFLINE")
        print("-" * 80)
        for device_id, device_data in offline_devices:
            is_current = device_id == local_device_id
            marker = " (this device)" if is_current else ""
            name = device_data.get("name", device_id)
            last_seen = format_time_ago(device_data.get("last_seen_at", 0))
            print(f"  {name}{marker}")
            print(f"    ID: {device_id}")
            print(f"    Last seen: {last_seen}")
            print()

    print("=" * 80)
    print(f"Total: {len(devices)} device(s)")
    print()


if __name__ == "__main__":
    main()
