#!/bin/bash

# Directory paths
BIN_DIR="$HOME/.local/bin"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

# Create directories if they don't exist
mkdir -p "$BIN_DIR"
mkdir -p "$SYSTEMD_USER_DIR"

echo "Installing fix-dock-icons script..."
cp fix-dock-icons.py "$BIN_DIR/fix-dock-icons"
chmod +x "$BIN_DIR/fix-dock-icons"

echo "Creating systemd service and path units..."

# Create service file
cat <<EOF > "$SYSTEMD_USER_DIR/fix-dock-icons.service"
[Unit]
Description=Fix dock icons for Wayland (Symlinks by StartupWMClass)

[Service]
Type=oneshot
ExecStart=$BIN_DIR/fix-dock-icons
EOF

# Create path file
cat <<EOF > "$SYSTEMD_USER_DIR/fix-dock-icons.path"
[Unit]
Description=Monitor application directories for new .desktop files to fix dock icons

[Path]
PathChanged=/usr/share/applications
PathChanged=/var/lib/flatpak/exports/share/applications
PathChanged=%h/.local/share/flatpak/exports/share/applications
PathChanged=%h/.local/share/applications

[Install]
WantedBy=default.target
EOF

echo "Reloading systemd daemon..."
systemctl --user daemon-reload

echo "Enabling and starting systemd path monitoring..."
systemctl --user enable --now fix-dock-icons.path

echo "Installation complete! The script is now running in the background."
echo "Logs can be found at: ~/.local/state/fix-dock-icons.log"
