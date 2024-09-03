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
from gpiozero import LED
import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

# Definición del arreglo de LEDs
led_array = LED(17)

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización del sensor AS7341
sensor = AS7341(board.I2C())

# Sensor ATIME (Por defecto es 100)
sensor.atime = 29

# Sensor ASTEP (Por defecto es 999)
sensor.astep = 599

# Sensor GAIN (Por defecto es 8 (128))
sensor.gain = 8

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# Registro log
log_register = "/home/pi/Raspi-Confgs/take_pictures.log"

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

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

def mostrar_datos():
    print("------ Datos de la muestra ------")

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

    print("------------------------------------------")

    datos = datos_sensor()
    # promedio_datos_medida(datos)
    hora_santiago = datetime.datetime.now(zona_santiago)
    datos_str = ",".join(map(str, datos))
    foto_id = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
    guardar_datos(datos_str, foto_id, hora_santiago)
    return datos

def guardar_datos(datos, foto_id, hora_santiago):

    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")
    foto_id = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

    datos = datos.split(",")
    # datos.append("")
    datos.append(foto_id)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    #with open(f"/home/pi/Data/DataSensor/data_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.csv", mode='a', newline='') as archivo_csv:
    with open(f"/home/pi/Data/DataSensor/data.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)
    
# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

# Función para tomar una foto y guardarla con h:m:s d:m:a
def tomar_foto():
	try:
		
		picam2.start()
		
		hora_santiago = datetime.datetime.now(zona_santiago)
		nombre_foto = f"/home/pi/Data/Photos/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

		fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
		picam2.capture_file(nombre_foto)
		time.sleep(2)
		#led_array.off()

	except Exception as e:
		print("Error al tomar la foto")
		limpiar_pantalla(hora_santiago)
		lcd.lcd_display_string("Error con foto", 2)

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

# Función para "limpiar" la pantalla LCD y además imprimir la hora
# en la primera fila
def limpiar_pantalla(hora_santiago):
	lcd.lcd_clear()
	lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)

# Función para llevar registro de los datos tomados
def register_data_log():
    hora_santiago = datetime.datetime.now(zona_santiago)    
    with open(log_register, "a") as log_file:
        log_file.write(f"Datos del sensor guardados a las {hora_santiago}\n")

# Función para llevar registro de las fotos tomadas
def register_log():
    hora_santiago = datetime.datetime.now(zona_santiago)
    with open(log_register, "a") as log_file:
        log_file.write(f"Foto tomada a las {hora_santiago}\n")

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------

def main():
    # Se define la hora a la que se esté tomando la foto y medición
    hora_santiago = datetime.datetime.now(zona_santiago)

    # Se llama a la función que toma la foto
    # Se deja registro en el log
    led_array.on()
    tomar_foto()
    register_log()

    # Se llama a la función para tomar datos
    # Se imprime mensaje en pantalla
    mostrar_datos()
    register_data_log()
    led_array.off()
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Datos y Foto OK", 2)
    time.sleep(2)

    # Se limpia la pantalla
    lcd.lcd_clear()


if __name__ == "__main__":
	main()
