# village
A portal to allow computers to talk to each other on the internet
(in the form of a server-like application)

# Philosophy

In a computer, there are a number of applications running. Other computers can connect to these applications and interact with them.

# Architecture

register_user -> register a user (idempotent, via Firebase token)
sign_in -> validate session and update last_sign_in_at
register_device -> register a device for a user
ask -> send a command string to a target device you own
respond -> send back output for that command

# Design decision

For the sake of simplicity and minimal development, we will use:
- Auth: Firebase Auth w/ Email/Password
- Database: Firebase Realtime Database
- Storage: Firebase Storage (if needed)
- Function: Firebase Cloud Functions

# Schema (minimal routing only)

The portal only authenticates the caller and routes messages. All validation and app existence checks happen on the destination device.

- users/{uid}
  - email, display_name, created_at

- devices/{device_id}
  - owner_uid, name, status, last_seen_at

- routes/{route_id}
  - from_uid, from_device_id
  - to_uid, to_device_id
  - command (string CLI command), created_at, status: pending|delivered|failed

- responses/{route_id}
  - from_device_id, output (string/JSON), content_type, created_at

Notes
- Auth: Firebase Auth (Email/Password). Clients run `register_user.py` which prompts for email/password - if account doesn't exist, it offers to create it automatically. Tokens are cached locally at `~/.village/auth.json` with automatic refresh. Functions verify tokens and enforce device ownership.
- Delivery: portal writes routes; destination devices should keep an RTDB listener on their route path for fast push delivery. Polling is only a fallback. Replies go to responses/{route_id}.
- Ingress: use HTTPS Cloud Functions for register_user, sign_in, register_device, ask, respond so server-side auth/validation wraps every write; the functions then write to RTDB.

# Device ID (minimal, permanent)
- On sign-up/sign-in, check for a local file (`~/.village/device_id` on Unix, `%APPDATA%\\village\\device_id` on Windows). If it exists, reuse the UUID inside.
- If missing, generate a UUIDv4, write it to that file, and keep it forever (delete only on explicit reset).
- Register `device_id` with the portal alongside the user’s auth token; portal rejects if that `device_id` is already claimed by another user.
