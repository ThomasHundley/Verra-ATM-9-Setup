#!/bin/bash
# Send warning to Minecraft players
screen -S atm9 -X stuff "say SERVER NOTICE: Scheduled restart in 60 seconds.\015"
sleep 30
screen -S atm9 -X stuff "say SERVER NOTICE: Restarting in 30 seconds!\015"
sleep 20
screen -S atm9 -X stuff "say SERVER NOTICE: Restarting in 10 seconds. See you in a few minutes!\015"
sleep 10
# Tell the system to restart the service
sudo systemctl restart atm9
