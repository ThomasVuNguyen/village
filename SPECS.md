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
- If Cloud Functions are used: one CF validates/auths and enqueues to Computer 2’s queue; Computer 2 polls; optional CF to push results to Computer 1 (else it polls).

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
