---
title: 'Quickstart: send your first command'
pubDate: '2025-12-01'
---

Get a sender and a listener talking in minutes.

## Install the CLI

```bash
npm install -g @thomasthemaker/village
```

Requirements: Node.js 16+ and Python 3.x available on PATH.

## Sign in and register this device

```bash
village setup
# prompts for email/password, caches token, registers device_id locally
```

The CLI saves your auth token at `~/.village/auth.json` (or `%APPDATA%\village\auth.json`) and your permanent `device_id` in the same folder.

## Start a listener on the target device

On the machine that should execute commands:

```bash
village listen
```

It polls Firebase RTDB every 100ms, executes commands with a 240s timeout, and posts results back to the portal.

## Send a command from another device

On your sender:

```bash
village send "echo hi"
# auto-routes to an idle device you own
```

You can target a specific device with `--to <device_id>` or set `TO_DEVICE_ID` and `COMMAND` env vars directly. The sender waits for the response and prints it.

## Clean up or rerun

- Check your devices: `village status`
- Keep auth but reset the device id: `village logout --reset`
- Stop a listener with `Ctrl+C` (it marks the device offline)
