#!/usr/bin/env python3
import os
import logging

LOG_FILE = os.path.expanduser("~/.local/state/fix-dock-icons.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s")

DIRECTORIES = [
    "/usr/share/applications",
    "/var/lib/flatpak/exports/share/applications",
    os.path.expanduser("~/.local/share/flatpak/exports/share/applications")
]

TARGET_DIR = os.path.expanduser("~/.local/share/applications")
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

def main():
    fixed_count = 0
    for directory in DIRECTORIES:
        if not os.path.exists(directory):
            continue
            
        for filename in os.listdir(directory):
            if not filename.endswith(".desktop"):
                continue
                
            filepath = os.path.join(directory, filename)
            if os.path.islink(filepath):
                continue
                
            wm_class = get_startup_wm_class(filepath)
            if not wm_class:
                continue
                
            base_name = filename[:-8]
            # Se la WM class è diversa dal nome del file
            if wm_class != base_name:
                symlink_name = f"{wm_class}.desktop"
                symlink_path = os.path.join(TARGET_DIR, symlink_name)
                
                # Crea il symlink se non esiste già
                if not os.path.exists(symlink_path):
                    try:
                        os.symlink(filepath, symlink_path)
                        logging.info(f"Fixed: Creato symlink {symlink_name} -> {filepath}")
                        print(f"Fixed: Creato symlink {symlink_name} -> {filepath}")
                        fixed_count += 1
                    except Exception as e:
                        logging.error(f"Errore nella creazione del symlink per {filename}: {e}")
                        
    if fixed_count == 0:
        print("Tutte le app sono già a posto.")
    else:
        print(f"Sistemate {fixed_count} applicazioni. Controlla {LOG_FILE} per i dettagli.")

if __name__ == "__main__":
    main()
