#!/bin/bash

# Define the log file path
LOGFILE="/home/pi/Raspi-Confgs/boot_log.log"

# Function to log messages with timestamps
log(){
   echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOGFILE
}

# Log the start of the script and execute cleanup_leds.py
# This is done to clean up the used leds in the previous reboot
log "RPI Initialization Routine: Running cleanup_leds.py"
python3 ~/Raspi-Confgs/cleanup_leds.py
sleep 2

# Log the start of the script and execute rpistart.py
# This is a test to verify the leds
log "RPI Initialization Routine: Running rpistart.py" 
python3 ~/Raspi-Confgs/rpistart.py
sleep 2

# Log the start of the script and execute upload_not_sent_data.py
# This is done to upload the data that haven't been sent cause
# ftp connection loss
log "RPI Initialization Routine: Running upload_not_sent_data.py"
sudo python3 ~/Raspi-Confgs/upload_not_sent_data.py
sleep 2

# Log the start of the script and execute remove_files.py
# This is done every day to remove the existing files in the pi sd
log "RPI Initialization Routine: Running remove_files.py"
sudo python3 ~/Raspi-Confgs/remove_files.py
sleep 2

# Log to continue with the execution of rpi_ftpsensor.py
log "RPI Initialization Routine: Proceeding to rpi_ftpsensor.py"
log "RPI Initialization Routine: Executing rpi_ftpsensor.py"
sudo python3 ~/Agrosuper-cb/rpi_ftpsensor.py
