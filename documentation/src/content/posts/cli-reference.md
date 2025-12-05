---
title: 'CLI Reference'
pubDate: '2025-12-02'
---

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

Flags:
- `village send --to <device_id>`: target a specific device (defaults to auto-route)
- `village send --no-wait`: fire and forget

Environment:
- `TO_DEVICE_ID`: set a target (`auto` picks an idle one)
- `COMMAND`: command string to run on the target

Notes:
- Device IDs stick to each machine unless you `--reset`.
- `send` waits by default; add `--no-wait` to fire-and-forget.
- Tokens refresh automatically; cached in `~/.village/auth.json` or `%APPDATA%\\village\\auth.json`.
