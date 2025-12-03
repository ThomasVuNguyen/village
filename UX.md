# Village UX (MVP)

## Goals
- One-command setup that makes a machine ready to talk to the village cloud.
- No flags; short positional commands; defaults favor speed over safety.
- Keep the user in the terminal with minimal prompts.

## Flow: first-time setup
1) User runs the one-command installer (per OS). It:
   - Installs CLI + background agent.
   - Ensures Python is available; creates/updates `village/venv/` if needed.
   - Writes Firebase config and `village/config.json` (uid, password, allowed apps).
2) User sets or edits the machine identity via CLI: `village set account_name ...` and `village set password ...`; duplicates uids are rejected by the cloud.
3) Agent starts (or is started by the installer) and begins heartbeating presence using the uid/password as the machine identity (not an interactive login).

## Flow: create an app on the device
1) User creates `app/village/main.py` with `def handler(event):`.
2) User installs any deps into `app/venv/` (optional).
3) Agent auto-detects the app (no publish step) because `village/main.py` exists.

## Flow: call an app from another machine
1) Caller runs `village call UID PASSWORD app arg1 arg2` (or uses stored machine identity from `config.json`).
2) CLI writes request to the cloud with `call_id` and `ts`.
3) Caller waits for response from the cloud; stale responses are dropped client-side.

## Flow: device handling inbound work
1) Agent sees request in its queue (for allowed app + uid).
2) Agent runs `handler(event)` with args/object, enforces per-call timeout.
3) Agent writes `{call_id, status, result|error_code|message}` back to the cloud.

## Flow: presence/offline
- Agent heartbeats `last_seen/status` every N seconds.
- Cloud marks `offline` quickly if stale; calls can be rejected early when offline.

## Flow: credentials
- Stored locally in `village/config.json`; no enforced file perms.
- UID/password identify the machine and do not expire by default; passwords may be passed positionally or set via `village set ...`.

## Flow: troubleshooting
- Check presence: `village logs app tail` (minimal local logs in `app/`).
- Common fixes: restart agent, verify `credentials.json`, confirm `venv/` exists.
