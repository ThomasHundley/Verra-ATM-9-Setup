#!/usr/bin/env python3
import os
import shutil
import subprocess
import time
import pwd
import grp
from datetime import datetime

# --- CONFIGURATION ---
SOURCE_DIR = "/var/atm9"
BACKUP_DIR = "/backup/atm9_daily"
TEMP_DIR = "/backup/atm9_staging"

# List of folders to exclude (Relative to the server folder)
EXCLUDE_DIRS = ["simplebackups", "mods", "libraries", "logs"] 

SERVICE_NAME = "atm9"
SCREEN_USER = "ascentius"      # The user who will own the backup files
MIN_FREE_GB = 10
SAFETY_FACTOR = 1.5                
# ---------------------

def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_dir_size(path):
    result = subprocess.run(['du', '-sb', path], stdout=subprocess.PIPE, text=True)
    return int(result.stdout.split()[0])

def manage_space(source_size):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        # Ensure the backup directory itself is owned by ascentius
        uid = pwd.getpwnam(SCREEN_USER).pw_uid
        gid = grp.getgrnam(SCREEN_USER).gr_gid
        os.chown(BACKUP_DIR, uid, gid)

    total, used, free = shutil.disk_usage(BACKUP_DIR)
    needed_space = source_size * SAFETY_FACTOR
    
    log(f"Disk Check - Free: {free // (1024**3)}GB | Needed: {needed_space // (1024**3)}GB")

    while free < needed_space or free < (MIN_FREE_GB * 1024**3):
        backups = sorted(
            [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith('.tar.gz')],
            key=os.path.getmtime
        )
        if not backups:
            log("WARNING: Cannot free up enough space! Proceeding anyway, but may fail.")
            break
            
        log(f"Deleting oldest backup to free space: {backups[0]}")
        os.remove(backups[0])
        total, used, free = shutil.disk_usage(BACKUP_DIR)

def send_warning():
    log("Sending 60-second warning to players...")
    cmd_prefix = ["sudo", "-u", SCREEN_USER, "screen", "-S", SERVICE_NAME, "-X", "stuff"]
    subprocess.run(cmd_prefix + [f"say SERVER NOTICE: Daily Backup & Restart in 60 seconds!\n"])
    time.sleep(30)
    subprocess.run(cmd_prefix + [f"say SERVER NOTICE: Restarting in 30 seconds!\n"])
    time.sleep(20)
    subprocess.run(cmd_prefix + [f"say SERVER NOTICE: Restarting in 10 seconds...\n"])
    time.sleep(10)

def main():
    log("=== Starting Daily Maintenance ===")
    
    source_size = get_dir_size(SOURCE_DIR)
    manage_space(source_size)
    send_warning()

    log(f"Stopping {SERVICE_NAME}...")
    subprocess.run(["systemctl", "stop", SERVICE_NAME])
    time.sleep(5)

    log(f"Rsyncing files to staging area...")
    rsync_cmd = ["rsync", "-a"]
    for item in EXCLUDE_DIRS:
        rsync_cmd.append(f"--exclude={item}")
    rsync_cmd.append(f"{SOURCE_DIR}/")
    rsync_cmd.append(f"{TEMP_DIR}/")

    try:
        subprocess.run(rsync_cmd, check=True)
    except subprocess.CalledProcessError as e:
        log(f"CRITICAL: Rsync failed: {e}")
        subprocess.run(["systemctl", "start", SERVICE_NAME])
        exit(1)

    log(f"Starting {SERVICE_NAME} back up...")
    subprocess.run(["systemctl", "start", SERVICE_NAME])

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"atm9_backup_{timestamp}.tar.gz"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    log(f"Compressing staging area into {filename}...")
    subprocess.run(["tar", "-czf", filepath, "-C", "/backup", os.path.basename(TEMP_DIR)])

    # --- THIS PART FIXES THE PERMISSIONS ---
    uid = pwd.getpwnam(SCREEN_USER).pw_uid
    gid = grp.getgrnam(SCREEN_USER).gr_gid
    os.chown(filepath, uid, gid)
    # ----------------------------------------

    log("Cleaning up staging area...")
    shutil.rmtree(TEMP_DIR)
    log("=== Daily Maintenance Complete ===")

if __name__ == "__main__":
    main()
