
import os
import sys
import requests
import subprocess
import time

# SETTINGS
GITHUB_REPO = "Tropikanogr/float_widget"
VERSION_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/version.txt"
EXE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest/download/float_widget_full_stats.exe"
LOCAL_VERSION_FILE = "version.txt"
LOCAL_EXE = "float_widget_full_stats.exe"
TEMP_EXE = "float_widget_tmp.exe"

def read_local_version():
    if not os.path.exists(LOCAL_VERSION_FILE):
        return "0.0"
    with open(LOCAL_VERSION_FILE, "r") as f:
        return f.read().strip()

def read_remote_version():
    try:
        r = requests.get(VERSION_URL, timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return None

def download_new_version():
    try:
        r = requests.get(EXE_URL, timeout=15)
        with open(TEMP_EXE, "wb") as f:
            f.write(r.content)
        os.replace(TEMP_EXE, LOCAL_EXE)
        return True
    except Exception as e:
        print("Download failed:", e)
        return False

def write_new_version(ver):
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(ver)

def run_app():
    subprocess.Popen([LOCAL_EXE])
    sys.exit()

def main():
    local_version = read_local_version()
    remote_version = read_remote_version()

    if remote_version and remote_version != local_version:
        print(f"🟡 Νέα έκδοση {remote_version} διαθέσιμη (τρέχουσα: {local_version})...")
        if download_new_version():
            write_new_version(remote_version)
            print("✅ Ενημέρωση ολοκληρώθηκε.")
            time.sleep(1)
        else:
            print("❌ Η λήψη απέτυχε. Εκκίνηση παλιάς έκδοσης.")
    else:
        print("✅ Τρέχεις την τελευταία έκδοση.")

    run_app()

if __name__ == "__main__":
    main()
