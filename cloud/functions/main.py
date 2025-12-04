import json
import time
from typing import Any, Dict, Optional

from firebase_admin import auth, db, initialize_app
from firebase_functions import https_fn

FIREBASE_URL = "https://village-app.firebaseio.com"

initialize_app(options={"databaseURL": FIREBASE_URL})


def _json_response(payload: Dict[str, Any], status: int = 200) -> https_fn.Response:
    return https_fn.Response(
        json.dumps(payload), status=status, mimetype="application/json"
    )


def _error(message: str, status: int = 400) -> https_fn.Response:
    return _json_response({"error": message}, status=status)


def _require_auth(req: https_fn.Request) -> Optional[Dict[str, Any]]:
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        return auth.verify_id_token(token)
    except Exception:
        return None


def _get_json(req: https_fn.Request) -> Optional[Dict[str, Any]]:
    data = req.get_json(silent=True)
    return data if isinstance(data, dict) else None


def _device_ref(device_id: str):
    return db.reference(f"devices/{device_id}")


def _route_ref(route_id: str):
    return db.reference(f"routes/{route_id}")


@https_fn.on_request()
def register_device(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return _error("Use POST", status=405)

    claims = _require_auth(req)
    if not claims:
        return _error("Unauthorized", status=401)

    data = _get_json(req)
    if not data:
        return _error("Invalid JSON", status=400)

    device_id = (data.get("device_id") or "").strip()
    name = (data.get("name") or "").strip()
    if not device_id:
        return _error("device_id required", status=400)

    uid = claims["uid"]
    ref = _device_ref(device_id)
    existing = ref.get()

    if existing and existing.get("owner_uid") != uid:
        return _error("device_id already claimed", status=403)

    now = int(time.time())
    ref.update(
        {
            "owner_uid": uid,
            "name": name or device_id,
            "status": "online",
            "last_seen_at": now,
            "created_at": existing.get("created_at", now) if existing else now,
        }
    )

    return _json_response({"device_id": device_id, "owner_uid": uid})


@https_fn.on_request()
def send_route(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return _error("Use POST", status=405)

    claims = _require_auth(req)
    if not claims:
        return _error("Unauthorized", status=401)

    data = _get_json(req)
    if not data:
        return _error("Invalid JSON", status=400)

    from_device_id = (data.get("from_device_id") or "").strip()
    to_device_id = (data.get("to_device_id") or "").strip()
    payload = data.get("payload")
    content_type = (data.get("content_type") or "application/json").strip()

    if not from_device_id or not to_device_id:
        return _error("from_device_id and to_device_id required", status=400)
    if payload is None:
        return _error("payload required", status=400)

    uid = claims["uid"]
    from_device = _device_ref(from_device_id).get()
    if not from_device or from_device.get("owner_uid") != uid:
        return _error("from_device_id not registered to caller", status=403)

    to_device = _device_ref(to_device_id).get()
    if not to_device:
        return _error("to_device_id not found", status=404)

    to_uid = to_device.get("owner_uid")
    now = int(time.time())
    routes_ref = db.reference("routes")
    route_ref = routes_ref.push(
        {
            "from_uid": uid,
            "from_device_id": from_device_id,
            "to_uid": to_uid,
            "to_device_id": to_device_id,
            "payload": payload,
            "content_type": content_type,
            "created_at": now,
            "status": "pending",
        }
    )

    return _json_response({"route_id": route_ref.key, "status": "pending"})


@https_fn.on_request()
def send_response(req: https_fn.Request) -> https_fn.Response:
    if req.method != "POST":
        return _error("Use POST", status=405)

    claims = _require_auth(req)
    if not claims:
        return _error("Unauthorized", status=401)

    data = _get_json(req)
    if not data:
        return _error("Invalid JSON", status=400)

    route_id = (data.get("route_id") or "").strip()
    from_device_id = (data.get("from_device_id") or "").strip()
    payload = data.get("payload")
    content_type = (data.get("content_type") or "application/json").strip()

    if not route_id or not from_device_id:
        return _error("route_id and from_device_id required", status=400)
    if payload is None:
        return _error("payload required", status=400)

    uid = claims["uid"]
    device = _device_ref(from_device_id).get()
    if not device or device.get("owner_uid") != uid:
        return _error("from_device_id not registered to caller", status=403)

    route = _route_ref(route_id).get()
    if not route:
        return _error("route not found", status=404)
    if route.get("to_device_id") != from_device_id:
        return _error("device not authorized to respond to this route", status=403)

    now = int(time.time())
    response_ref = db.reference(f"responses/{route_id}")
    if response_ref.get():
        return _error("response already exists for this route", status=409)

    response_ref.set(
        {
            "from_device_id": from_device_id,
            "payload": payload,
            "content_type": content_type,
            "created_at": now,
        }
    )
    _route_ref(route_id).update({"status": "delivered"})

    return _json_response({"route_id": route_id, "status": "delivered"})
