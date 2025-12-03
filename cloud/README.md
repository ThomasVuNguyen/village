This is the cloud service for the village network.

Functionality:
- Store and manage credentials for devices
- Route requests and responses to the appropriate device
- Automatically load credentials and applications
- Fast

Specs:
- Firebase realtime db
- Simple GCP stuff, firebase preferable
- Firebase cloud functions

Deploy (rules only):
- `firebase deploy --only database:village-app --project comfyshare-a8fd8` (uses `cloud/firebase.json` + `cloud/.firebaserc`).
