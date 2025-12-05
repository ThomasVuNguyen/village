---
title: 'Architecture (deep dive)'
pubDate: '2025-12-03'
---

If you’re curious what’s under the hood.

- Cloud: Firebase Auth + Realtime Database + Cloud Functions. Functions only verify you own the devices and route messages.
- Device IDs: Permanent per machine (stored in `~/.village/device_id` or `%APPDATA%\\village\\device_id`), reused unless you reset.
- Flow: `send` writes a route; `listen` polls routes, executes locally (stdin closed), posts response; `send` polls responses.
- Status: listeners mark devices `idle`, `busy`, `offline` around execution; `status` reads them.
- Timeouts: commands have a 240s cap; stderr is included in the response.
