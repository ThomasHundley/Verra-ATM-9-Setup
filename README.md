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
