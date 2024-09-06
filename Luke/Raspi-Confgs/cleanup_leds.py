import RPi.GPIO as GPIO
import logging
import datetime
import time
import pytz
from gpiozero import LED

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

led_red = LED(26)

log_file_path = "/home/pi/Raspi-Confgs/boot_log.log"

# List all GPIO pins that are connected to LEDs
led_pins = [5, 6, 17, 22, 26, 27]  # Replace these with your actual GPIO pin numbers

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

def main():

    logger = setup_logger()
    led_pins = [5, 6, 17, 22, 26, 27, ]

    try:
        log_with_time(logger, "Cleaning up the GPIO Pins")
        for pin in led_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        led_red.on()
        time.sleep(2)
        led_red.off()

        GPIO.cleanup()
        log_with_time(logger, "GPIO Cleaned, ready to use")
        print("Pines GPIO limpiados")

    except Exception as e:

        log_with_time(logger, f"An error occurred while cleaning the GPIO Pins: {e}")


if __name__ == "__main__":
    main()
