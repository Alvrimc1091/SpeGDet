import os
import logging
import datetime
import time
import pytz

log_file_path = "/home/pi/logs/split_logs.log"

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


def split_log_file(log_file_path):
    logger = setup_logger()

    # Extract the base name of the log file (e.g., 'boot_log.log')
    base_name = os.path.basename(log_file_path)

    log_with_time(logger, f"RPI Initialization Routine: Opening {log_file_path} to save it")
    with open(log_file_path, 'r') as log_file:
        lines = log_file.readlines()

    logs_by_date = {}
    
    # Separate logs by date
    for line in lines:
        if len(line) > 10:  # Ensure line is long enough to contain a date
            date = line[:10]  # Extract the date part (YYYY-MM-DD)
            if date in logs_by_date:
                logs_by_date[date].append(line)
            else:
                logs_by_date[date] = [line]


    # Check the number of unique dates
    if len(logs_by_date) == 1:
        print(f"There is only one unique date in the {log_file_path} file. No separate log files will be created.")
        log_with_time(logger, f"RPI Initialization Routine: There's only one unique date in {log_file_path} file. Nothing done")
        return

    log_with_time(logger, "RPI Initialization Routine: Moving the log data of the previous day into a new file")

    # Write each date's logs to a new file and remove them from the original log file
    with open(log_file_path, 'w') as log_file:
        for date, logs in sorted(logs_by_date.items()):
            if logs:  # Check if there are logs for that date
                date_log_filename = f"/home/pi/logs/{date}_{base_name}"
                with open(date_log_filename, 'a') as date_log_file:
                    date_log_file.writelines(logs)
                log_with_time(logger, f"RPI Initialization Routine: Log data saved in {date_log_filename}")
            
            # Only keep logs for the latest date in the original log file
            if date == max(logs_by_date.keys()):
                log_file.writelines(logs)

        #log_with_time(logger, f"RPI Initialization Routine: Log data saved in {date_log_filename}")

def main(): 
    logger = setup_logger()
    log_files = ["/home/pi/logs/boot_log.log", "/home/pi/logs/rpisensor.log", "/home/pi/logs/log_rpiftpsensor.log", "/home/pi/logs/split_logs.log"]
    #log_file_path = "/home/pi/Raspi-Confgs/test_rpisensor.log"
    #split_log_file(log_file_path)

    for log_file_path in log_files:
        split_log_file(log_file_path) 

if __name__ == "__main__":
    main()
