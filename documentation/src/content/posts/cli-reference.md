---
title: 'CLI reference'
pubDate: '2025-12-02'
---

All commands are thin Node wrappers around the Python core.

```bash
village setup              # Sign up/sign in and register this device
village register [name]    # Register this device with optional name
village listen             # Start listening for incoming commands
village send <command>     # Send to an idle device (auto-route by default)
village send <command> --to <device_id>  # Target a specific device
village status             # Show your devices + status/last seen
village logout             # Clear cached auth (keeps device_id)
village logout --reset     # Clear auth and delete device_id file
village version | -v       # Show installed CLI version
```

Environment variables:

- `TO_DEVICE_ID`: set a target (`auto` or empty triggers idle-device routing)
- `COMMAND`: raw command string to execute on the target

Notes:

- Device IDs are permanent per machine unless you `--reset`.
- `listen` uses 100ms polling, marks the device busy while executing, and posts the output via the `respond` Cloud Function.
- `send` waits for a response by polling `responses/{route_id}` unless you pass `--no-wait`.
- Auth tokens refresh automatically; cached at `~/.village/auth.json` or `%APPDATA%\village\auth.json`.
