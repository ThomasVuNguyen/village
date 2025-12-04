import time
from typing import Any, Dict

import bcrypt
from firebase_admin import db, initialize_app
from firebase_functions import https_fn

FIREBASE_URL = "https://village-app.firebaseio.com"

initialize_app(options={"databaseURL": FIREBASE_URL})

# sign_up

# sign_in

# request

# respond
