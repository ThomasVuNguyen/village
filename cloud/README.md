This is the cloud service for the village network.

Functionality:
- Store and manage credentials for devices
- Route requests and responses to the appropriate device
- Automatically load credentials and applications
- Fast

Specs:
- Firebase realtime db
- Simple GCP stuff, firebase preferable
- Firebase cloud functions

Deploy (rules only):
- `firebase deploy --only database:village-app --project comfyshare-a8fd8` (uses `cloud/firebase.json` + `cloud/.firebaserc`).

Cloud portal (Functions, Python):
- HTTP function `portal` in `cloud/functions/main.py` checks uid/password, app allowlist, presence, enqueues to `/requests/{uid}/{call_id}`, and short-polls `/responses` to return a result (or `queued`).
- Credentials expected at `/credentials/{uid}` with `password_hash` (bcrypt) and optional `apps: [..]`.
- Deploy portal: `firebase deploy --only functions --project comfyshare-a8fd8`.
