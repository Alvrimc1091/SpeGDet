#!/bin/bash

# Define the log file path
LOGFILE="/home/pi/Raspi-Confgs/rpisensor.log"

# Function to log messages with timestamps
log(){
   echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOGFILE
}

# Log the start of remove_files.py
log "RPI Routines: remove_files.py (Removes files from the RPI db)"
sudo python3 ~/Raspi-Confgs/remove_files.py
sleep 1
