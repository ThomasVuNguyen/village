# Village Tech Spec (MVP)

## Runtime model
- Code layout: `village/main.py` containing `def handler(event):` that returns JSON-serializable data.
- Env: user-managed `venv/` beside `village/`; runtime activates it before invoking `handler`.
- Dependencies: user preinstalls all deps into `venv/`; no automatic install.

## Auth & security (minimal)
- Transport: HTTPS everywhere.
- Credentials: store password hashes (e.g., bcrypt), not plaintext.
- Per-app ACL: each `uid` declares allowed `app` names; reject others.
- No rate limiting (yet); add basic backoff/lockout on repeated failures if possible.

## Request/response contract
- Request (JSON): `{uid, password, app, args: [..] | object, call_id, ts}`; `call_id` unique per call, `ts` client timestamp.
- Response (JSON): `{call_id, status: ok|error|offline|timeout, result?, error_code?, message?}`.
- Clients drop stale responses (older than their request `ts`).

## Transport flow
- Preferred minimal path: Computer 1 writes request to Firebase; Computer 2 runs a listener (long-poll/WebSocket) on its queue, processes via `handler`, writes result back; Computer 1 listens for result.

## Presence/offline
- Computer 2 heartbeats `{status, last_seen}` to Firebase every N seconds.
- If `last_seen` too old, return `status=offline` quickly. Optional: queue with TTL; otherwise reject when offline.

## Limits & safety
- Cap request/response size to Firebase RTDB max per write; truncate/reject with `error_code=payload_too_large`.
- Default per-call timeout (e.g., 30s); mark `timeout` status.
- Sanitize output before storing in Firebase.

## Logging/audit
- Minimal audit per call in Firebase: `uid, app, call_id, timestamps, status`.
- Full logs stay local on Computer 2; Firebase only stores summaries.

## CLI shape (no flags)
- Positional forms; document clearly. Examples: `village login UID PASSWORD`, `village call UID PASSWORD app arg1 arg2`, `village logs app tail`.
- Provide `config set key value` so users can avoid retyping passwords; avoid putting passwords in shell history when possible.

## Platform notes
- Linux first. Mac next. Windows: prefer WSL; native Windows needs adjusted venv activation paths.

## Risks & assumptions (MVP)
- Installation is a one-command installer per OS but still undefined; assumes Python and a sibling `venv/` are present/created and that Firebase creds/config succeed without rollback on partial failures.
- Credentials never expire by default and are stored locally in `village/credentials.json`; users must protect that file (and their backups) because there is no rotation/reset story yet, and we are not enforcing file permissions.
- Requests rely on client timestamps only; no server-side nonce/window to prevent replay, and passwords are sent on every call.
- User apps run without sandboxing or resource limits; code/dependency integrity is not validated before execution.
- Offline/queue TTL handling is optional; callers may hang on dead workers. Assumes light load so Firebase RTDB limits/quotas are not a concern for now.
- CLI uses positional arguments, so credentials can land in shell history; consider `config set` plus prompting/masking even though secrets are persisted to `credentials.json`.

## Architecture boundaries (for clarity)
- Central cloud village: Firebase RTDB plus portal/routing entrypoint that validates requests and enqueues to the correct user machine.
- Device agent: installed via one command; sets up local runtime, stores credentials in `village/credentials.json`, sends calls to the cloud, listens for inbound work, executes `village/main.py:handler`, and posts results back.
- App discovery on a device is implicit/automatic based on local presence of `village/main.py`; no explicit publish step in MVP.

## App (device) MVP spec
- Lives in `app/` with `village/main.py` (and optional `venv/`); if present and the agent is running, the app is callable.
- One-command installer sets up CLI + agent, writes `village/credentials.json` (uid/password/app list) and Firebase config needed to reach the cloud.
- Agent heartbeats presence, listens for requests, invokes `handler(event)`, applies per-call timeout, writes responses, and keeps minimal local logs.
- CLI uses positional commands (`login`, `call`, `logs`, `config set`) reading credentials from `village/credentials.json`; passwords can still be passed positionally.

## Cloud (backend) MVP spec
- Lives in `cloud/`; uses Firebase RTDB for queues/presence/responses and an HTTPS ingress to authenticate and enqueue.
- Ingress validates uid/password, checks app is allowed and presence is fresh, then writes the request to RTDB with `call_id` and `ts`.
- Device writes `{call_id, status, result|error_code|message}` to responses; clients poll/read and drop stale results by `ts`.
- Presence tracked per `uid` (`last_seen/status`); ingress returns `offline` if stale.
