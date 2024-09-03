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
    log "RPI Reboot Routine: Python script rpi_ftpsensor.py stopped successfully."
else
    log "RPI Reboot Routine: Failed to stop Python script rpi_ftpsensor.py."
fi

# Wait a short period to ensure the script is terminated
log "RPI Reboot Routine: Waiting for 10 seconds to ensure the script is terminated."
sleep 10

# Execute cleanup_leds to later run a clossing routine
log "RPI Reboot Routine: Running cleanup_leds.py"
python3 ~/Raspi-Confgs/cleanup_leds.py
sleep 1

# Execute turnon_red_led.py to indicate that the rpi will reboot
log "RPI Reboot Routine: Running "
python3 ~/Raspi-Confgs/red_led_blink.py

# Reboot the system
log "Rebooting the system."
sudo reboot
