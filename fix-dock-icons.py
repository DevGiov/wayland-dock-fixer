#!/usr/bin/env python3
import os
import logging
import stat

# Use XDG_STATE_HOME for logs if available, default to ~/.local/state
xdg_state_home = os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state"))
LOG_FILE = os.path.join(xdg_state_home, "fix-dock-icons.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

# Determine data directories using XDG variables for universal compatibility
xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":")
xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))

# Directories to scan for .desktop files
DIRECTORIES = []
for d in xdg_data_dirs:
    DIRECTORIES.append(os.path.join(d, "applications"))
    
# Add Flatpak and Snap common paths
DIRECTORIES.extend([
    "/var/lib/flatpak/exports/share/applications",
    os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
    "/var/lib/snapd/desktop/applications"
])

# Remove duplicates while preserving order
DIRECTORIES = list(dict.fromkeys(DIRECTORIES))

TARGET_DIR = os.path.join(xdg_data_home, "applications")
os.makedirs(TARGET_DIR, exist_ok=True)

def get_startup_wm_class(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            in_desktop_entry = False
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_desktop_entry = True
                elif line.startswith("[") and in_desktop_entry:
                    break
                
                if in_desktop_entry and line.startswith("StartupWMClass="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def create_symlink(filepath, symlink_path):
    # If it exists and is a symlink, check if it points to the correct file
    if os.path.islink(symlink_path):
        if os.readlink(symlink_path) == filepath:
            return False
        # Remove old symlink to update it
        os.remove(symlink_path)
    elif os.path.exists(symlink_path):
        # It's a real file, do not overwrite user modifications
        return False
        
    try:
        os.symlink(filepath, symlink_path)
        msg = f"Fixed: Created symlink {os.path.basename(symlink_path)} -> {filepath}"
        logging.info(msg)
        print(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to create symlink for {filepath}: {e}")
        return False

def main():
    fixed_count = 0
    for directory in DIRECTORIES:
        if not os.path.isdir(directory):
            continue
            
        for filename in os.listdir(directory):
            if not filename.endswith(".desktop"):
                continue
                
            filepath = os.path.join(directory, filename)
            # Skip symlinks to avoid circular resolution or parsing our own generated files
            if os.path.islink(filepath):
                continue
                
            wm_class = get_startup_wm_class(filepath)
            if not wm_class:
                continue
                
            base_name = filename[:-8]
            
            # Sometimes Wayland and XWayland differ in case (e.g., Spotify vs spotify).
            # We create symlinks for both the exact wm_class and lowercase version to maximize compatibility across different docks/compositors.
            names_to_link = set()
            if wm_class != base_name:
                names_to_link.add(wm_class)
            if wm_class.lower() != base_name.lower():
                names_to_link.add(wm_class.lower())
                
            for name in names_to_link:
                symlink_name = f"{name}.desktop"
                symlink_path = os.path.join(TARGET_DIR, symlink_name)
                
                # Prevent symlinking to itself in the same directory
                if os.path.abspath(filepath) == os.path.abspath(symlink_path):
                    continue
                    
                if create_symlink(filepath, symlink_path):
                    fixed_count += 1
                        
    if fixed_count == 0:
        print("Everything is up to date. No new app icons to fix.")
    else:
        print(f"Fixed {fixed_count} application icon(s). Check {LOG_FILE} for details.")

if __name__ == "__main__":
    main()
