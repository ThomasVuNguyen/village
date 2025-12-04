# Milestone 1

Build a functional village cloud + app. The installation can be complex and manual - that's ok.

Just needs to work on Linux machines

## How to use (Milestone 1, manual)
- Prereqs: Linux, Python 3, Firebase project configured with RTDB rules and Cloud Function `portal` deployed.
- App setup: `cd app && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Configure machine identity: `python -m village.cli set account_name YOUR_UID` and `python -m village.cli set password YOUR_PW` (writes `app/village/config.json`; Firebase URL defaults to `https://village-app.firebaseio.com`).
- Run the device agent: `python -m village.cli run` (listens for requests, heartbeats presence, executes `village/main.py`).
- Caller flow: from another machine, run `python -m village.cli call YOUR_UID YOUR_PW app arg1 arg2` to enqueue via the cloud and wait for a response (30s timeout).
- Cloud expectations: `/credentials/{uid}` in RTDB contains `password_hash` (bcrypt) and optional `apps` allowlist; `portal` function validates uid/password/app and writes to `/requests/{uid}/{call_id}`, short-polling `/responses/{uid}/{call_id}`.


# Milestone 2

Iterate and improve

# Milestone 3

Build installation experience
