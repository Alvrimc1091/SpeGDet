#/usr/local/bin/open_anydesk.sh (log in /var/log/open_anydesk.log) 
#(configured to start on boot with crontab)

#!/bin/bash

# Define the log file path
LOGFILE="/var/log/open_anydesk.log"

# Function to log messages with timestamps
log(){
   echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> $LOGFILE
}

log "Starting Anydesk"
/usr/bin/anydesk
log "Anydesk Started"

log "Opening Data Luke folder"
xdg-open /home/alvaro/Documents/Workspace/Granos/FTP/Data_luke
log "Data Luke folder opened"

log "Opening Data Leia folder"
xgd-open /home/alvaro/Documents/Workspace/Granos/FTP/Data_Leia
log "Data Leia folder opened"
