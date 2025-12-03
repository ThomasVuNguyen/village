# village
Computers talking to each other on the internet

# Idea
village - how computers can talk to each other on the internet

village is a portal.

Computer #1 calls to a portal with 4 pieces of information:
- uid
- password
- app name
- variables

the portal uses uid & password to route to another computer, namely computer #2

The computer #2 then runs the app with the app name & variables, send back the result through the portal.

Computer #1 receives the result.

user experience:

sign up:
'bash install village'
'village sign up' - enter name + pw

create app
- write a file
(app name, variables, login & output)
- auto-deploy & ready to be called

request
'village tungid tungpw appname(12,23)'

# Design decisions

apps will be written in Python (similar to cloud functions)
support Linux first, then Mac OS, last Windows
no flag in the cli commands unless absolutely necessary (it's ugly and breaks the flow)

# Frustration-free experience (for users)

Installation
- apt on Linux
- homebrew on MacOS (later)
- chocolate on Windows (later)

# Hosting / Centralized service
- Everything hosted on Firebase realtime db

# Milestone 1 quick start (Linux, manual)
- Ensure Python 3 is installed; create/activate a venv in `app/venv` and `pip install -r app/requirements.txt`.
- Set machine identity (writes `app/village/config.json`): `python -m village.cli set account_name YOUR_UID` and `python -m village.cli set password YOUR_PW`. Firebase URL defaults to `https://village-app.firebaseio.com`.
- Run the agent from `app/`: `python -m village.cli run` (listens for requests, heartbeats presence, writes responses).
- From another machine, call your app and wait for result: `python -m village.cli call YOUR_UID YOUR_PW app arg1 arg2` (defaults to 30s wait).
