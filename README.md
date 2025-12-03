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
