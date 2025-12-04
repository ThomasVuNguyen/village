"""
Helper to obtain a Firebase ID token automatically.

Priority:
1) Use cached token in ~/.village/auth.json (or %APPDATA%\\village\\auth.json) if still valid.
2) Refresh using cached refresh_token + FIREBASE_API_KEY (or FIREBASE_REFRESH_TOKEN override).
3) If none, auto sign up anonymously using FIREBASE_API_KEY and cache tokens.
4) Fall back to ID_TOKEN env var (manual).
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from firebase_config import API_KEY as CONFIG_API_KEY

AUTH_FILE = (
    Path(os.environ["APPDATA"]) / "village" / "auth.json"
    if os.name == "nt"
    else Path.home() / ".village" / "auth.json"
)
API_KEY = os.environ.get("FIREBASE_API_KEY", "").strip() or CONFIG_API_KEY
ENV_REFRESH_TOKEN = os.environ.get("FIREBASE_REFRESH_TOKEN", "").strip()


def _load_cache() -> Dict[str, Any]:
    if not AUTH_FILE.exists():
        return {}
    try:
        return json.loads(AUTH_FILE.read_text())
    except Exception:
        return {}


def _save_cache(id_token: str, refresh_token: str, expires_in: int) -> None:
    expires_at = int(time.time()) + max(int(expires_in), 0) - 60  # refresh 1m early
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(
        json.dumps(
            {
                "id_token": id_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
            }
        )
    )


def _refresh_id_token(refresh_token: str) -> Optional[str]:
    if not API_KEY or not refresh_token:
        return None
    resp = requests.post(
        f"https://securetoken.googleapis.com/v1/token?key={API_KEY}",
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        timeout=15,
    )
    if resp.status_code != 200:
        return None
    payload = resp.json()
    id_token = payload.get("id_token")
    new_refresh = payload.get("refresh_token", refresh_token)
    expires_in = int(payload.get("expires_in", 3600))
    if id_token:
        _save_cache(id_token, new_refresh, expires_in)
    return id_token


def _sign_up_anonymous() -> Optional[str]:
    if not API_KEY:
        return None
    resp = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",
        json={"returnSecureToken": True},
        timeout=15,
    )
    if resp.status_code != 200:
        return None
    payload = resp.json()
    id_token = payload.get("idToken")
    refresh_token = payload.get("refreshToken", "")
    expires_in = int(payload.get("expiresIn", 3600))
    if id_token and refresh_token:
        _save_cache(id_token, refresh_token, expires_in)
    return id_token


def get_id_token(auto_create: bool = True) -> str:
    cache = _load_cache()
    now = time.time()
    cached_token = cache.get("id_token")
    expires_at = cache.get("expires_at", 0)
    refresh_token = cache.get("refresh_token") or ENV_REFRESH_TOKEN

    if cached_token and expires_at > now + 30:
        return cached_token

    # Try refresh flow
    refreshed = _refresh_id_token(refresh_token)
    if refreshed:
        return refreshed

    if auto_create:
        created = _sign_up_anonymous()
        if created:
            return created

    env_token = os.environ.get("ID_TOKEN", "").strip()
    if env_token:
        return env_token

    raise SystemExit(
        "No ID token available. Set FIREBASE_API_KEY (and optional FIREBASE_REFRESH_TOKEN) "
        "or set ID_TOKEN env manually."
    )
