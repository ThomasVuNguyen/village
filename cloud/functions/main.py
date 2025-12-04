import time
from typing import Any, Dict

import bcrypt
from firebase_admin import db, initialize_app
from firebase_functions import https_fn

FIREBASE_URL = "https://village-app.firebaseio.com"

initialize_app(options={"databaseURL": FIREBASE_URL})


def _check_password(given: str, stored: str) -> bool:
    if not stored:
        return False
    try:
        if stored.startswith("$2"):
            return bcrypt.checkpw(given.encode("utf-8"), stored.encode("utf-8"))
    except Exception:
        return False
    return given == stored


def _allowed_app(app: str, creds: Dict[str, Any]) -> bool:
    apps = creds.get("apps") or []
    return not apps or app in apps


def _presence_ok(uid: str, max_age: int = 60) -> bool:
    presence = db.reference(f"presence/{uid}").get()
    if not presence:
        return False
    last_seen = presence.get("last_seen", 0)
    return (time.time() - last_seen) <= max_age


@https_fn.on_request()
def portal(req: https_fn.Request) -> https_fn.Response:
    body = req.get_json(silent=True) or {}
    uid = body.get("uid", "")
    password = body.get("password", "")
    app = body.get("app", "")
    args = body.get("args", [])

    if not uid or not password or not app:
        return https_fn.Response("missing uid/password/app", status=400)

    creds = db.reference(f"credentials/{uid}").get()
    if not creds:
        return https_fn.Response("auth_failed", status=401)
    stored_pw = creds.get("password_hash") or creds.get("password") or ""
    if not _check_password(password, stored_pw):
        return https_fn.Response("auth_failed", status=401)
    if not _allowed_app(app, creds):
        return https_fn.Response("app_not_allowed", status=403)
    if not _presence_ok(uid):
        return https_fn.Response("offline", status=503)

    call_id = body.get("call_id") or str(int(time.time() * 1000))
    ts = int(time.time())
    request_payload = {
        "uid": uid,
        "app": app,
        "args": args,
        "call_id": call_id,
        "ts": ts,
    }
    db.reference(f"requests/{uid}/{call_id}").set(request_payload)

    # Optional short poll for a response to return immediately
    timeout = 25
    start = time.time()
    while time.time() - start < timeout:
        resp = db.reference(f"responses/{uid}/{call_id}").get()
        if resp:
            return https_fn.Response(resp, mimetype="application/json")
        time.sleep(1)

    return https_fn.Response({"status": "queued", "call_id": call_id}, mimetype="application/json")
