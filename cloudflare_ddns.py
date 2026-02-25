import requests
import os
from datetime import datetime

# --- CONFIGURATION ---
ZONE_ID = "ID"
API_TOKEN = "TOKEN"
DOMAIN_NAME = "verramc.com"  # The record you want to update
IP_FILE_PATH = "/home/ascentius/current_ip.txt"
# ---------------------

def log(message):
    print(f"[{datetime.now()}] {message}")

def get_current_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except Exception as e:
        log(f"Error fetching public IP: {e}")
        return None

def get_last_known_ip():
    if not os.path.exists(IP_FILE_PATH):
        return None
    with open(IP_FILE_PATH, "r") as f:
        return f.read().strip()

def save_new_ip(ip):
    with open(IP_FILE_PATH, "w") as f:
        f.write(ip)

def update_cloudflare(new_ip):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Step 1: Get the Record ID for verramc.com
    list_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records?type=A&name={DOMAIN_NAME}"
    try:
        records = requests.get(list_url, headers=headers).json()
        if not records['success'] or len(records['result']) == 0:
            log("Error: Could not find DNS record in Cloudflare.")
            return False
        
        record_id = records['result'][0]['id']
        
        # Step 2: Update the record
        update_url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
        payload = {
            "content": new_ip,
            "name": DOMAIN_NAME,
            "type": "A",
            "proxied": False
        }
        
        response = requests.put(update_url, headers=headers, json=payload).json()
        
        if response['success']:
            log(f"Success! Updated Cloudflare A-Record to {new_ip}")
            return True
        else:
            log(f"Cloudflare Update Failed: {response['errors']}")
            return False

    except Exception as e:
        log(f"Exception during Cloudflare update: {e}")
        return False

# --- MAIN LOGIC ---
if __name__ == "__main__":
    public_ip = get_current_public_ip()
    stored_ip = get_last_known_ip()

    if public_ip is None:
        log("Could not get public IP. Aborting.")
        exit()

    if public_ip != stored_ip:
        log(f"IP Change Detected! Old: {stored_ip} -> New: {public_ip}")
        success = update_cloudflare(public_ip)
        
        if success:
            save_new_ip(public_ip)
            log("Local IP file updated.")
    else:
        # IP is the same, do nothing
        pass
