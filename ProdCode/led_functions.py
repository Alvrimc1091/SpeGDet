import csv
import socket
import math
import time
import threading
import os
import board
import time
import datetime
import zoneinfo
import numpy as np
import pandas as pd
from gpiozero import LED

led_red = LED(5) # Rojo -> Alerta
led_green = LED(6) # Verde -> Trigo
led_blue = LED(22) # Azul -> Poroto
led_yellow = LED(27) # Amarillo -> Maíz

timeslp = 0.2
times = 3

def encender_led(led):
    """Enciende un LED durante 2 segundos."""
    if led is not None:
        led.on()
        time.sleep(2)
        led.off()

def secuencia_led_inicializacion(timevar):

    for i in range(3):
        
        timevar = timeslp
        led_red.on()
        time.sleep(timeslp)
        led_red.off()
        led_green.on()
        time.sleep(timeslp)
        led_green.off()
        led_yellow.on()
        time.sleep(timeslp)
        led_yellow.off()
        led_blue.on()
        time.sleep(timeslp)
        led_blue.off()

def blink_leds(counts):
    
    counts = times

    for i in range(counts):
        led_red.on()
        led_blue.on()
        led_green.on()
        led_yellow.on()
        time.sleep(timeslp)
        led_red.off()
        led_blue.off()
        led_green.off()
        led_yellow.off()
    
#secuencia_led_inicializacion(timeslp)
#blink_leds(times)
#encender_led(led_red)