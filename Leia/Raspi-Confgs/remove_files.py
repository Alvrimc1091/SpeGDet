import os
import time
import datetime
import logging
import pytz

log_file_path = "/home/pi/logs/rpisensor.log"

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


def check_and_remove_files(folder_path):
    logger = setup_logger()
    try:
        # Check if the folder is empty
        if not os.listdir(folder_path):
            log_with_time(logger, f"The folder {folder_path} is empty. Nothing done.")
            print(f"The folder '{folder_path}' is empty.")
            return

        # Remove files in the folder
        for filename in os.listdir(folder_path):
            log_with_time(logger, f"Removing files from {folder_path}")
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Removed: {filename}")
        log_with_time(logger, f"Files removed from {folder_path}")
        print("All files have been removed from the folder.")

    except Exception as e:
        log_with_time(logger, f"An error occurred: {e}")
        print(f"An error occurred: {e}")

def main():
    # Specify the folder path to check and remove files
    folder_to_check = "/home/pi/Agrosuper-cb/TestMeassures/"

    check_and_remove_files(folder_to_check)

if __name__ == "__main__":
    main()
