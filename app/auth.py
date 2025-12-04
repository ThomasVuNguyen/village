"""
Helper to obtain a Firebase ID token via email/password authentication.

Priority:
1) Use cached token in ~/.village/auth.json (or %APPDATA%\\village\\auth.json) if still valid.
2) Refresh using cached refresh_token + FIREBASE_API_KEY.
3) Prompt for email/password and sign in via Firebase Auth.
4) Fall back to ID_TOKEN env var (manual).
"""

import getpass
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


def _sign_in_with_password(email: str = None, password: str = None) -> Optional[str]:
    """Sign in with email/password via Firebase Auth REST API. Creates account if needed."""
    if not email:
        email = input("Email: ").strip()
    if not password:
        password = getpass.getpass("Password: ")

    if not email or not password:
        print("Email and password required")
        return None

    # Try sign in first
    resp = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=15,
    )

    # If account doesn't exist, create it
    if resp.status_code != 200:
        error_data = resp.json().get("error", {})
        error_msg = error_data.get("message", "")

        if "INVALID_LOGIN_CREDENTIALS" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
            create = input(f"Account {email} not found. Create it? (y/n): ").strip().lower()
            if create == "y":
                if len(password) < 6:
                    print("Password must be at least 6 characters")
                    return None

                # Create account
                signup_resp = requests.post(
                    f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}",
                    json={"email": email, "password": password, "returnSecureToken": True},
                    timeout=15,
                )

                if signup_resp.status_code != 200:
                    signup_error = signup_resp.json().get("error", {}).get("message", "Unknown error")
                    print(f"Account creation failed: {signup_error}")
                    return None

                print(f"Account created: {email}")
                resp = signup_resp
            else:
                print("Sign in cancelled")
                return None
        else:
            print(f"Sign in failed: {error_msg}")
            return None

    payload = resp.json()
    id_token = payload.get("idToken")
    refresh_token = payload.get("refreshToken")
    expires_in = int(payload.get("expiresIn", 3600))

    if id_token and refresh_token:
        _save_cache(id_token, refresh_token, expires_in)
        return id_token

    print("Sign in response missing tokens")
    return None


def get_id_token(
    auto_create: bool = True, email: str = None, password: str = None
) -> str:
    """Get Firebase ID token with priority fallback."""
    cache = _load_cache()
    now = time.time()
    cached_token = cache.get("id_token")
    expires_at = cache.get("expires_at", 0)
    refresh_token = cache.get("refresh_token") or os.environ.get(
        "FIREBASE_REFRESH_TOKEN", ""
    ).strip()

    # Priority 1: Use cached token if still valid
    if cached_token and expires_at > now + 30:
        return cached_token

    # Priority 2: Try refresh flow
    refreshed = _refresh_id_token(refresh_token)
    if refreshed:
        return refreshed

    # Priority 3: Sign in with email/password
    if auto_create:
        created = _sign_in_with_password(email, password)
        if created:
            return created

    # Priority 4: Fall back to env var
    env_token = os.environ.get("ID_TOKEN", "").strip()
    if env_token:
        return env_token

    raise SystemExit(
        "No ID token available. Sign in with email/password or provide FIREBASE_REFRESH_TOKEN or ID_TOKEN env var."
    )
