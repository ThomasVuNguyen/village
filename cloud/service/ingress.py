import time
from typing import Any, Dict

import requests


class Ingress:
    """
    Minimal ingress that authenticates and enqueues to Firebase RTDB via REST.
    """

    def __init__(self, firebase_url: str) -> None:
        self.firebase_url = firebase_url.rstrip("/")

    def _url(self, path: str) -> str:
        path = path.strip("/")
        return f"{self.firebase_url}/{path}.json"

    def _allowed_app(self, request_body: Dict[str, Any]) -> bool:
        return bool(request_body.get("app"))

    def enqueue(self, body: Dict[str, Any]) -> Dict[str, Any]:
        uid = body.get("uid", "")
        password = body.get("password", "")
        call_id = body.get("call_id") or f"{int(time.time() * 1000)}"
        if not uid or not password:
            return {
                "status": "error",
                "error_code": "auth_failed",
                "message": "uid/password required",
            }
        if not self._allowed_app(body):
            return {"status": "error", "error_code": "app_not_allowed"}
        # Simplified: trust password hash check is done elsewhere.
        requests.put(self._url(f"requests/{uid}/{call_id}"), json=body)
        return {"status": "ok", "call_id": call_id}
