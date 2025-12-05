---
title: 'Quickstart: use Village'
pubDate: '2025-12-01'
---

Everything you need to send a command between two of your devices.

## 1) Install the CLI

```bash
npm install -g @thomasthemaker/village
```

Requirements: Node.js 16+ and Python 3.x on PATH.

## 2) Sign in and register this device

```bash
village setup
# prompts for email/password, caches token, registers device_id locally
```

## 3) Start a listener on the target device

On the machine that will run commands:

```bash
village listen
```

Leave it running; it will execute incoming commands and return the output.

## 4) Send a command from another device

On your sender (any of your signed-in devices):

```bash
village send "echo hi"
# auto-routes to an idle device you own
```

You can target a specific device with `--to <device_id>` or set `TO_DEVICE_ID` and `COMMAND` env vars directly. The sender waits for the response and prints it.

## 5) Handy checks

- Check devices: `village status`
- Reset auth/device id: `village logout --reset`
- Stop a listener with `Ctrl+C`

## Troubleshooting

- Error “from_device_id not registered to caller”: run `village register` on the sending machine.
- No idle devices: start `village listen` on a device, or target one explicitly with `--to <device_id>`.
- Need the installed version: `village -v`.
