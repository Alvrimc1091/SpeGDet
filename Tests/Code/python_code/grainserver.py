# RPI Zero 2W funcionará como servidor, PC como cliente

# --------
# Servidor
# --------

# Debe enviar datos del sensor y proyectar resultado en pantalla
# Datos y foto deben ser guardados en SD
# Se puede crear rutina para subir los datos al Github

# TO DO
# Establecer conexión servidor (RPI) - cliente (PC)
# Guardar datos en .csv de la misma forma que se hace actualmente
# Realizar calibración y estimación de granos


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

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

def guardar_foto():
    try:
        while True:
            hora_santiago = datetime.datetime.now()  # Obtiene la hora actual
            fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")            
            nombre_foto = f"foto_up_{fecha_hora_actual}.jpg"

            with open(nombre_foto, "ab") as f:  # Modo "ab" para escritura binaria y anexar
                f.write(data)
                print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada como {nombre_foto}")
            
            foto_id = f"foto_up_{fecha_hora_actual}.jpg"
            datos_a_csv("", foto_id)
    
    except Exception as e:
        print("Error al recibir la foto:", e)

def guardar_datos_sensor():
    try:
        while True:
            data = ",".join(map(str, datos_sensor()))  # Obtener datos del sensor y convertirlos a cadena
            hora_santiago = datetime.datetime.now(zona_santiago)

            foto_id = f"foto_up_{hora_santiago.strftime("%H%M%S_%d%m%Y")}.jpg"
            datos_a_csv(data, foto_id)

            lcd.lcd_display_string("Datos guardados:", 1)
            lcd.lcd_display_string(f"{hora_santiago.strftime('%H:%M:%S')}", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")

            time.sleep(60)  # Envía datos cada 3 segundos

    except Exception as e:
        print("Error sending data:", e)

def datos_a_csv(datos, foto_id):
    datos = datos.split(",")

    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    datos.append(foto_id)

    with open("data_test.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)


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

# ------
# Procesamiento para estimar el grano
# ------