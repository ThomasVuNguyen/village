# Village 🏘️

Distributed inter-device communication - send commands between your computers and get responses back automatically.

## Installation

```bash
npm install -g village
```

**Requirements:**
- Node.js 16+
- Python 3.x

## Quick Start

**1. Setup (first time)**
```bash
village setup
# Enter email & password
# Device auto-registered
```

**2. Start listener (on devices that will execute commands)**
```bash
village listen
# Runs in foreground, waits for incoming commands
```

**3. Send commands (from any device)**
```bash
# Auto-route to any idle device
village send "uptime"

# Target specific device
village send "df -h" --to device-id-here

# Check your devices
village status
```

## Commands

```bash
village setup              # Sign up/sign in and register this device
village register [name]    # Register this device with optional name
village send <command>     # Send command to idle device (auto-routes)
village listen             # Start listening for incoming commands
village status             # Show all your devices and their status
village logout             # Sign out (keeps device_id)
village logout --reset     # Full reset (deletes device_id)
```

## Examples

```bash
# One-to-one: Target specific device
village send "nvidia-smi" --to laptop-device-id

# One-to-many: Auto-route to idle device
village send "python train.py"

# Check which devices are available
village status
```

## How It Works

1. **Device A** sends command via `village send`
2. **Firebase RTDB** routes the command
3. **Device B** (running `village listen`) executes it
4. **Device A** receives and displays the output

Fast, secure, simple.

## Architecture

- **CLI**: Node.js wrapper (distribution)
- **Backend**: Python (Firebase + command execution)
- **Cloud**: Firebase Realtime Database + Cloud Functions

## License

MIT
