"""
Sign in (validate token) against the portal; updates last_sign_in_at. Automatically uses Google device flow if no token cached.

Usage:
  set SIGN_IN_URL=<override_endpoint_optional>
  python sign_in.py
"""

import os

import requests
from auth import get_id_token

DEFAULT_URL = "https://sign-in-wprnv4rl5q-uc.a.run.app"
SIGN_IN_URL = os.environ.get("SIGN_IN_URL", DEFAULT_URL)


def main() -> None:
    id_token = get_id_token()

    resp = requests.post(
        SIGN_IN_URL,
        headers={"Authorization": f"Bearer {id_token}"},
        json={},
        timeout=15,
    )
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
