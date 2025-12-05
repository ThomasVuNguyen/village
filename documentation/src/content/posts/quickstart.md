---
title: 'Quick Start: If you have two or more computers/servers'
pubDate: '2025-12-01'
---
This tutorial assumes you have two or more computers/servers.

They can be physical or virtual machines, on-premises or in the cloud. They can be on different networks or even in different countries. All you need is a working internet connection on both computers.

In this guide, you will learn how to connect two devices and send commands between them.

## 1) Install the CLI on Computer #1

```bash
npm install -g @thomasthemaker/village
```

Requirements: Node.js 16+ and Python 3.x.

## 2) Sign in and register Computer #1

```bash
village setup
```

You will be prompted to enter an email & password for login. And your Computer will be registered in the village network under your account.

## 3) Start a listener on the target device

On the machine that will run commands:

```bash
village listen
```

This will allow other computers under your account to send command to Computer #1.

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
This will send the command to Computer #1 from Computer #2!

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
