# Wayland Dock Fixer

This tool automatically fixes issues with pinned applications disappearing or duplicating icons in Wayland docks. 

## The Problem
Wayland compositors use `app_id` to identify running applications. However, some applications (like Flatpaks or specifically packaged binaries) provide `.desktop` files whose names differ from the actual `app_id`. When you pin these apps, the dock expects a `.desktop` file matching the `app_id`. If it's missing, the app may not stay pinned upon restarting the dock, or it might spawn a duplicate generic icon when launched.

## The Solution
This tool consists of a Python script that scans standard `.desktop` directories (`/usr/share/applications/`, `/var/lib/flatpak/...`) and reads the `StartupWMClass` (which usually equals the Wayland `app_id`). If there's a mismatch between the filename and the `StartupWMClass`, it automatically generates a symlink in `~/.local/share/applications/` matching the correct `app_id`. 

A systemd user service and path monitor are set up to run this automatically in the background whenever an application is installed, removed, or updated.

## Installation

Run the installation script to deploy the python script and configure the background systemd service:

```bash
chmod +x install.sh
./install.sh
```

## Logs
The script operates silently in the background. You can check what it fixed by reading the log file:
```bash
cat ~/.local/state/fix-dock-icons.log
```
