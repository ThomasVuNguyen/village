import json
import time
from typing import Any, Dict, Optional

import requests


class FirebaseTransport:
    """
    Minimal RTDB REST transport. The caller must provide a `firebase_url`
    ending with `.json` root (e.g., https://<project>.firebaseio.com).
    """

    def __init__(self, firebase_url: str, api_key: str = "") -> None:
        self.firebase_url = firebase_url.rstrip("/")
        self.api_key = api_key

    def _url(self, path: str) -> str:
        path = path.strip("/")
        return f"{self.firebase_url}/{path}.json"

    def heartbeat(self, uid: str, status: str = "online") -> None:
        payload = {"status": status, "last_seen": int(time.time())}
        requests.patch(self._url(f"presence/{uid}"), json=payload)

    def enqueue_request(self, uid: str, call_id: str, body: Dict[str, Any]) -> None:
        requests.put(self._url(f"requests/{uid}/{call_id}"), json=body)

    def write_response(self, uid: str, call_id: str, body: Dict[str, Any]) -> None:
        requests.put(self._url(f"responses/{uid}/{call_id}"), json=body)

    def read_next_request(self, uid: str, app: str) -> Optional[Dict[str, Any]]:
        # Simple poll for the first pending request for this app.
        resp = requests.get(self._url(f"requests/{uid}"))
        if resp.status_code != 200:
            return None
        data = resp.json() or {}
        for call_id, req in data.items():
            if req.get("app") == app:
                return {"call_id": call_id, "request": req}
        return None

    def ack_request(self, uid: str, call_id: str) -> None:
        requests.delete(self._url(f"requests/{uid}/{call_id}"))


def drop_stale_response(ts_request: int, ts_response: int) -> bool:
    return ts_response < ts_request
