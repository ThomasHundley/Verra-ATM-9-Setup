# Verra-ATM-9-Setup

Automated deployment and backup scripts for a heavily modded Minecraft server on Ubuntu

## 🛠️ Tech Stack & Hardware
* **OS:** Ubuntu Server 22.04 LTS (Headless)
* **Hardware:**  i7 4790k 32GB RAM, 1TB NVMe SSD, 1 TB HDD (backup)
* **Game Engine:** Forge 1.20.1 (Java 17)
* **Networking:** Cloudflare DNS with custom Python DDNS

## 📂 Repository Contents

### 1. Automation & Maintenance (`*.py`)
* `daily_maintenance.py`: A Python script triggered by a Systemd timer at 4:00 AM. It gracefully warns players via `screen`, stops the service, performs a fast `rsync` to a secondary HDD, restarts the server, and handles GZIP compression in the background to minimize downtime.
* `cloudflare_ddns.py`: A script running via cronjob every 10 minutes to detect ISP IP changes and dynamically update Cloudflare A-Records via API.

### 2. Systemd Services (`*.service`, `*.timer`)
* Custom daemon configurations used to keep the server alive, handle crash-restarts, and schedule automated maintenance tasks without manual intervention.

## 📂 Directory Structure
To recreate this server environment, files must be placed in their specific directories with appropriate permissions:

* **`/var/atm9/`**: Main Minecraft server directory.
  * Contains `server.properties`, `user_jvm_args.txt`, `startserver.sh`, and `restart_script.sh`.
* **`/home/ascentius/`**: Admin home directory for automation.
  * Contains `daily_maintenance.py` and `cloudflare_ddns.py`.
* **`/etc/systemd/system/`**: Linux system services.
  * Contains all `.service` and `.timer` files.
* **`/backup/atm9_daily/`**: Secondary HDD mount point for cold-storage `.tar.gz` backups.

---

## ⚙️ Installation & Setup Guide

### 1. Place the Scripts
Move the Python and Bash scripts to their respective directories and make them executable:
```bash
sudo chmod +x /home/ascentius/daily_maintenance.py
sudo chmod +x /var/atm9/restart_script.sh
