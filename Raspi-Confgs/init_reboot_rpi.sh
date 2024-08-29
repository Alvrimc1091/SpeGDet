#!/bin/bash

# Define the log file path
LOGFILE="/home/pi/Raspi-Confgs/boot_log.log"

# Function to log messages with timestamps
log(){
   echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOGFILE
}

# Log the start of the script
log "RPI Initialization Routine: Running cleanup_leds.py"
python3 ~/Raspi-Confgs/cleanup_leds.py
sleep 1

log "RPI Initialization Routine: Running rpistart.py" 
python3 ~/Raspi-Confgs/rpistart.py
sleep 1

log "RPI Initialization Routine: Running upload_not_sent_data.py"
sudo python3 ~/Raspi-Confgs/upload_not_sent_data.py
sleep 1
