# Script para tomar datos de la muestra

import socket
import time
import threading
import os
import board
import time
import datetime
import zoneinfo
import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización del sensor AS7341
sensor = AS7341(board.I2C())

sensor.led = 

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# Definición bar_graph()
# Obtiene las lecturas de los 10+1 canales
def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

# Función para obtener los datos del sensor
def datos_sensor():
    # Obtiene las lecturas de los canales y los almacena en un diccionario
    datos_sensor = [
        bar_graph(sensor.channel_415nm),
        bar_graph(sensor.channel_445nm),
        bar_graph(sensor.channel_480nm),
        bar_graph(sensor.channel_515nm),
        bar_graph(sensor.channel_555nm),
        bar_graph(sensor.channel_590nm),
        bar_graph(sensor.channel_630nm),
        bar_graph(sensor.channel_680nm),
        bar_graph(sensor.channel_clear),
        bar_graph(sensor.channel_nir)
    ]
    return datos_sensor

def tomar_datos():
    print("Datos de la muestra")

    print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
    print("F2 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
    print("F3 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
    print("F4 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
    print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
    print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
    print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
    print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
    print("Clear              %s" % bar_graph(sensor.channel_clear))
    print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))
    print("\n------------------------------------------------")

def tomar_foto():

    try:
        picam2.start()    
        hora_santiago = datetime.datetime.now(zona_santiago)
        nombre_foto = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        
        picam2.capture_file()
        time.sleep(2)

        with open(nombre_foto, "rb") as f:
            data = f.read()
            #print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {nombre_foto} guardada")        

    except Exception as e:
        print("Error al tomar la foto")

def main():

    hora_santiago = datetime.datetime.now(zona_santiago)

    tomar_datos()
    tomar_foto()

    lcd.lcd_clear()
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string("Datos guardados", 2)
    time.sleep(3)

    lcd.lcd_clear()
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string("Foto Guardada", 2)
    time.sleep(3)


if __name__ == "__main__":
    main()

