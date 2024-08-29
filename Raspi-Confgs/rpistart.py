from led_functions import *
import logging
import pytz
import datetime

times = 4
time_slp = 0.2

# Configuración del logger
def setup_logger():
    logger = logging.getLogger('MeasurementLogger')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('/home/pi/Raspi-Confgs/boot_log.log')
    formatter = logging.Formatter('%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def log_with_time(logger, message):
    """Log the message with the local time of Santiago de Chile."""
    chile_tz = pytz.timezone('Chile/Continental')
    now = datetime.datetime.now(chile_tz)
    logger.info(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {message}")

def main():
    logger = setup_logger()
    counts = 1
    try:
       secuencia_encendido_leds()
       secuencia_encendido_leds_inverso()
       blink_leds(counts)
       log_with_time(logger, "RPI Initialized.")

    except Exception as e:
       log_with_time(logger, f"Error while initializing RPI: {e}")
       return

if __name__ == "__main__":
    main()
