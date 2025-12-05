---
title: 'Identity, auth, and device lifecycle'
pubDate: '2025-12-04'
---

## Identity and auth

- Firebase Email/Password for user auth; the CLI prompts and caches tokens.
- Tokens live in `auth.json` with refresh support; refreshed automatically when close to expiry.
- The ID token is sent as `Authorization: Bearer <token>` to every Cloud Function.

## Device IDs

- Each machine gets a UUIDv4 stored at `~/.village/device_id` or `%APPDATA%\\village\\device_id`.
- The same ID is reused on subsequent runs; only deleted via `village logout --reset`.
- Cloud rejects registering a `device_id` that is already owned by another user.

## Listener behavior

- Fast polls `routes` every 100ms.
- Marks status `busy` while executing; `idle` after sending a response; `offline` on exit/cleanup.
- Executes with `stdin` redirected to `DEVNULL` to avoid hanging interactive commands.
- Captures stdout and stderr; includes stderr under a `[stderr]` marker in the response.
- Per-command timeout: 240s.

## Operational tips

- Register every device before sending: `village register "my-laptop"`.
- If you see `from_device_id not registered to caller`, register the sender device.
- If RTDB queries ever error, the listener falls back to fetching all routes and filtering locally.
- Keep both Python and Node up to date on every machine for smooth installs.
