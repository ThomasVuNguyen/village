"""
Register a user with the portal (idempotent). Automatically signs up anonymously with Firebase if needed and caches the token locally.

Usage:
  set FIREBASE_API_KEY=<firebase_web_api_key>
  set FIREBASE_REFRESH_TOKEN=<refresh_token>  # optional; otherwise anonymous sign-up is used
  set REGISTER_USER_URL=<override_endpoint_optional>
  python register_user.py
"""

import os

import requests
from auth import get_id_token

DEFAULT_URL = "https://register-user-wprnv4rl5q-uc.a.run.app"
REGISTER_USER_URL = os.environ.get("REGISTER_USER_URL", DEFAULT_URL)


def main() -> None:
    id_token = get_id_token()

    resp = requests.post(
        REGISTER_USER_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={},
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
