import logging
import time
import pytz
import os
from ftplib import FTP
import datetime
from gpiozero import LED

# Set the GPIO mode
led_red = LED(26)

# FTP server details
ftp_server = "192.168.0.102"
port = 2121
username = "leia"
password = "qwerty"

# Directories
failed_upload_dir = "/home/pi/Agrosuper-cb/TestMeassures/Failed_to_send_data"
remote_path = "~/Documents/Workspace/Granos/FTP/Data_leia"
log_file_path = "/home/pi/Raspi-Confgs/boot_log.log"

# Configuración del logger
def setup_logger():
    logger = logging.getLogger('MeasurementLogger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_with_time(logger, message):
    chile_tz = pytz.timezone('Chile/Continental')
    now = datetime.datetime.now(chile_tz)
    logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {message}")


def connect_to_ftp():
    logger = setup_logger()
    try:
        ftp = FTP()
        ftp.connect(ftp_server, port)
        ftp.login(user=username, passwd=password)
        log_with_time(logger, "Connected to the FTP Server")
        print("Connection established with the FTP server")
        return ftp
    except Exception as e:
        log_with_time(logger, f"Failed to connect or login to FTP server: {e}")
        print(f"Failed to connect or login to FTP server: {e}")
        return None

def upload_files(ftp):
    logger = setup_logger()
    try:
       # Check if the directory is empty
       # if not os.listdir(failed_upload_dir):
       #     log_with_time(logger, "No files to upload. The failed_upload_dir is empty.")
       #     return 
       # List all files in the failed upload directory
        for filename in os.listdir(failed_upload_dir):
            local_file_path = os.path.join(failed_upload_dir, filename)

            # Check if it is a file and upload it
            if os.path.isfile(local_file_path):
                with open(local_file_path, 'rb') as file:
                    ftp.storbinary(f'STOR {filename}', file)
                    log_with_time(logger, f"Uploaded {filename} to {remote_path}")
                    print(f"Uploaded {filename} to {remote_path}")

        log_with_time(logger, "All files have been uploaded successfully.")
    except Exception as e:
        log_with_time(f"Failed to upload files: {e}")
        print(f"Failed to upload files: {e}")


def remove_failed_uploaded_files(logger):
   logger = setup_logger()
   try:
        # Check if the directory is empty
        if not os.listdir(failed_upload_dir):
            log_with_time(logger, "No files to remove. The failed_upload_dir is empty.")
            print("There are no files to be removed")
            return

        for filename in os.listdir(failed_upload_dir):
            file_path = os.path.join(failed_upload_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                log_with_time(logger, f"Removed {filename} from {failed_upload_dir}")
                print(f"Files removed from {failed_upload_dir}")

        log_with_time(logger, "All uploaded files have been removed from the failed_upload_dir.")

   except Exception as e:
        log_with_time(logger, f"Failed to remove files: {e}")
        print(f"Failed to remove files: {e}")

def main():
    logger = setup_logger()
    led_red.on()
    # Connect to the FTP server
    log_with_time(logger, "Connecting to the FTP server")
    ftp = connect_to_ftp()
    if ftp:
        # Upload files if connected
        log_with_time(logger, "Uploading data (.csv and .jpg)")
        upload_files(ftp)

        # Remove files
        log_with_time(logger, "Removing data from the failed directory")
        remove_failed_uploaded_files(logger)

        # Close the FTP connection
        ftp.quit()
        log_with_time(logger, "FTP connection closed.")

    time.sleep(5)
    led_red.off()

if __name__ == "__main__":
    main()
