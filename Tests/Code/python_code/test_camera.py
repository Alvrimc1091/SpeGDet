from picamera2 import Picamera2, Preview 
import time 
import datetime
import zoneinfo
import board
import I2C_LCD_driver
from adafruit_as7341 import AS7341
import csv
import os

# ------------ Definición de AS7341 como variable "sensor"
i2c = board.I2C() 
sensor = AS7341(i2c)

# ------------ Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# ------------ Definición de cámara como variable "picam2"
picam2 = Picamera2()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Configuración de la cámara
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

lcd.lcd_clear()
lcd.lcd_display_string('Inicio de Medición', 1)
time.sleep(2)
lcd.lcd_clear()

# ------------ Definición de cámara como variable "picam2"
def iniciar_camara():
    picam2.start()

# Función para tomar una foto y mostrar el mensaje en la pantalla LCD
def tomar_foto():

    # Obtener datos horarios
    hora_santiago = datetime.datetime.now(zona_santiago)
    hora = hora_santiago.hour
    mins = hora_santiago.minute
    secs = hora_santiago.second
    
    iniciar_camara()  # Iniciar la cámara
    time.sleep(1)  # Esperar un momento para que la cámara se inicie correctamente
    
    # Tomar la foto
    lcd.lcd_display_string('Foto tomada', 1)
    picam2.capture_file(f"{hora}:{mins}:{secs}.jpg")
    lcd.lcd_clear()
    lcd.lcd_display_string(f"Guardada en", 1)
    lcd.lcd_display_string(f"{hora}:{mins}:{secs}.jpg", 2)

# ------------ Definición obtener_datos_sensor()
# ------------ Obtener los datos del sensor
def obtener_datos_sensor():
    datos_sensor = {
        'channel_415nm': sensor.channel_415nm,
        'channel_445nm': sensor.channel_445nm,
        'channel_480nm': sensor.channel_480nm,
        'channel_515nm': sensor.channel_515nm,
        'channel_555nm': sensor.channel_555nm,
        'channel_590nm': sensor.channel_590nm,
        'channel_630nm': sensor.channel_630nm,
        'channel_680nm': sensor.channel_680nm,
    }
    return datos_sensor

# ------------ Definición bar_graph()
# ------------ Obtiene las lecturas de los 10+1 canales
def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

# Función para mostrar los datos del sensor en pantalla
def mostrar_datos():
    # Muestra el resultado de las lecturas de los canales
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

# Función para escribir los datos en un archivo CSV
def escribir_csv(hora, datos_sensor):
    nombre_archivo = "datos_sensor.csv"
    existe_archivo = os.path.exists(nombre_archivo)

    with open(nombre_archivo, mode='a', newline='') as archivo_csv:
        campos = ['día', 'hora', 'violeta', 'indigo', 'blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'clear', 'near ir']
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)

        if not existe_archivo:
            escritor_csv.writeheader()

        escritor_csv.writerow({
            'día': hora.strftime("%Y-%m-%d"),
            'hora': hora.strftime("%H:%M:%S"),
            'violeta': datos_sensor['channel_415nm'],
            'indigo': datos_sensor['channel_445nm'],
            'blue': datos_sensor['channel_480nm'],
            'cyan': datos_sensor['channel_515nm'],
            'green': datos_sensor['channel_555nm'],
            'yellow': datos_sensor['channel_590nm'],
            'orange': datos_sensor['channel_630nm'],
            'red': datos_sensor['channel_680nm'],
            'clear': datos_sensor['channel_clear'],
            'near ir': datos_sensor['channel_nir']
        })

# Bucle infinito para repetir el proceso cada 10 segundos
while True:
    tomar_foto()  # Tomar una foto y mostrar el mensaje en la pantalla LCD
    datos_sensor = obtener_datos_sensor()  # Obtener los datos del sensor
    escribir_csv(hora_santiago, datos_sensor)  # Escribir los datos en el archivo CSV
    mostrar_datos(datos_sensor)  # Mostrar los datos del sensor en pantalla
    time.sleep(10)  # Esperar 10 segundos antes de repetir el ciclo