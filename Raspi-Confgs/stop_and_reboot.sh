#!/bin/bash
# stop_and_reboot.sh

# Define the log file path
LOGFILE="/home/pi/Raspi-Confgs/boot_log.log"

# Function to log messages with timestamps
log() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOGFILE
}

# Log the start of the script
log "Script started."

# Stop the Python script
if sudo pkill -f rpi_ftpsensor.py; then
    log "Python script rpi_ftpsensor.py stopped successfully."
else
    log "Failed to stop Python script rpi_ftpsensor.py."
fi

# Wait a short period to ensure the script is terminated
log "Waiting for 10 seconds to ensure the script is terminated."
sleep 10

# Reboot the system
log "Rebooting the system."
sudo reboot

