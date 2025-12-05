---
title: 'Architecture and data model'
pubDate: '2025-12-03'
---

Village keeps the cloud thin: authenticate, route, and return output. Devices own execution and validation.

## Cloud Functions (Firebase)

- `register_user` / `sign_in`: accept Firebase ID token, ensure `users/{uid}` exists, update `last_sign_in_at`.
- `register_device`: claim a `device_id` for the caller, writing `devices/{device_id}` with owner, name, status, timestamps.
- `ask`: validate ownership of `from_device_id` and `to_device_id`, then create `routes/{route_id}` with `status: pending`.
- `respond`: validate the responding device matches the route target, then write `responses/{route_id}` and mark the route delivered.

RTDB base URL: `https://village-app.firebaseio.com`.

## Schema highlights

- `users/{uid}`: `email`, `display_name`, `created_at`, `last_sign_in_at`
- `devices/{device_id}`: `owner_uid`, `name`, `status` (`idle|busy|offline`), `last_seen_at`, `created_at`
- `routes/{route_id}`: `from_uid`, `from_device_id`, `to_uid`, `to_device_id`, `command`, `content_type`, `created_at`, `status`
- `responses/{route_id}`: `from_device_id`, `output`, `content_type`, `created_at`

## Device flow

1) **Sender** posts `ask` with `from_device_id`, target device (explicit or auto-routed), and `command`.
2) **Listener** polls `routes`, filters for its device id + `pending`, sets itself `busy`, executes the command locally, and posts `respond`.
3) **Sender** polls `responses/{route_id}` and prints output.

## Routing and status

- Auto-routing picks the most recently seen idle device (excluding self).
- Listener updates its status to `idle` at start, `busy` during execution, and `offline` on exit.
- Commands time out after 240 seconds in the listener; stderr is included after a `[stderr]` marker.
