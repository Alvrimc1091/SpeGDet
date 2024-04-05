import socket
import os
import threading
from picamera2 import Picamera2, Preview
import time
import datetime
import zoneinfo
import csv
import json
import board
import I2C_LCD_driver
from adafruit_as7341 import AS7341

# Dirección y puerto del servidor
HOST = '192.168.2.15'
PORT = 8080

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Definción de AS7341 como "sensor"
i2c = board.I2C()
sensor = AS7341(i2c)

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización de pantalla LCD
lcd.lcd_clear()
lcd.lcd_display_string("Inicio de ", 1)
lcd.lcd_display_string("mediciones", 2)
time.sleep(2)
lcd.lcd_clear()

# Función para enviar datos del sensor al servidor
def enviar_datos_sensor(datos_sensor):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        datos = ",".join(map(str, datos_sensor))
        s.sendall(datos.encode())

        hora_santiago = datetime.datetime.now(zona_santiago)
        hora = hora_santiago.hour
        mins = hora_santiago.minute
        secs = hora_santiago.second

        lcd.lcd_display_string("Datos enviados:", 1)
        lcd.lcd_display_string(f"{hora_santiago.strftime('%H:%M:%S')}", 2)
        print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor enviados al servidor")


# Función para enviar la foto tomada por la cámara al servidor
def enviar_foto():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT + 1))
        picam2.start()
        time.sleep(1)
        hora_santiago = datetime.datetime.now(zona_santiago)
        picam2.capture_file("foto.jpg")
        with open("foto.jpg", "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                s.sendall(data)
        print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto enviada al servidor")


# Definición bar_graph()
# Obtiene las lecturas de los 10+1 canales
def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

# Función para obtener los datos del sensor
def obtener_datos_sensor():
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



# Bucle infinito para enviar datos y fotos continuamente
while True:
    hora_santiago = datetime.datetime.now(zona_santiago)
    datos_sensor = obtener_datos_sensor()
    enviar_datos_sensor(datos_sensor)
    enviar_foto()
    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos y foto enviados al servidor")

    time.sleep(5)  # Esperar 10 segundos antes de enviar nuevamente

