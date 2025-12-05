---
title: 'Quickstart'
pubDate: '2025-12-01'
---
You need 2+ machines (physical or virtual, anywhere, any network). 

For examples:
- A laptop at home.
- A computer at work.
- Servers in the cloud.
- Your grandma's old computer.

Just make sure they are connected to the internet. We will make them talk to each other.

## 1) Install the CLI on Computer #1

```bash
npm install -g @thomasthemaker/village
```

Requirements: Node.js 16+ and Python 3.x.

## 2) Sign in and register Computer #1

```bash
village setup
```

You will be prompted to enter an email & password for login. This registers the computer under your account. Repeat this on every device you want to use.

## 3) Start a listener on Computer #1

On the machine that will run commands:

```bash
village listen
```

This marks the device idle and ready to receive commands.

## 4) On Computer #2, perform the same setup

```bash
npm install -g @thomasthemaker/village
village setup
```

## 5) Send a command from another device

On your sender (any of your signed-in devices):

```bash
village send "ls"
# auto-routes to an idle device you own
```
Village will route the command to one of your idle listener devices (at random). The “message” is just the terminal command string; the response is exactly what the command prints (stdout + stderr).

Repeat this process with any additional devices/servers.

If you have more than 2 devices and want to send commands to Computer #2, you can use the `--to` flag:

```bash
village send "ls" --to <device_id>
```

## 6) Handy checks

- Check devices: `village status`
- Reset auth/device id: `village logout --reset`
- Stop a listener with `Ctrl+C`

## Troubleshooting

- Error "from_device_id not registered to caller": run `village register` on the sending machine.
- No idle devices: start `village listen` on a device, or target one explicitly with `--to <device_id>`.
- Need the installed version: `village -v`.
