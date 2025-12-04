"""
Register a user with the portal (idempotent; uses Firebase ID token).

Usage:
  set ID_TOKEN=<firebase_id_token>
  set REGISTER_USER_URL=<override_endpoint_optional>
  python register_user.py
"""

import os

import requests

DEFAULT_URL = "https://register-user-wprnv4rl5q-uc.a.run.app"
REGISTER_USER_URL = os.environ.get("REGISTER_USER_URL", DEFAULT_URL)


def main() -> None:
    id_token = os.environ.get("ID_TOKEN")
    if not id_token:
        raise SystemExit("ID_TOKEN env var is required (Firebase ID token).")

    resp = requests.post(
        REGISTER_USER_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={},
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
