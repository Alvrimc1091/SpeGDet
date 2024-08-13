# Script para tomar datos de la muestra
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
#import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

# Definición del arreglo de LEDs
led_array = LED(17) # LEDs de iluminación para el sensor

led_red = LED(5) # Rojo
led_green = LED(6) # Verde
led_blue = LED(22) # Azul
led_yellow = LED(27) # Amarillo

# Definición de pantalla LCD como variable "lcd"
#lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización del sensor AS7341
sensor = AS7341(board.I2C())

# Valores de Ganancia 

#   Parámetro      ||   Valor
# sensor.gain = 0  ||     0.5
# sensor.gain = 1  ||      1
# sensor.gain = 2  ||      2
# sensor.gain = 3  ||      4
# sensor.gain = 4  ||      8
# sensor.gain = 5  ||      16
# sensor.gain = 6  ||      32
# sensor.gain = 7  ||      64
# sensor.gain = 8  ||      128
# sensor.gain = 9  ||      256
# sensor.gain = 10 ||      512

# Sensor ATIME (Por defecto es 100)
sensor.atime = 29

# Sensor ASTEP (Por defecto es 999)
sensor.astep = 599

# Sensor GAIN (Por defecto es 8 (128))
sensor.gain = 8

# Definición de contador total de muestras
meassurement = 1

# Definición del threshold
threshold = 0.2

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# -------------------------------------------------------------------
# ----------------- Base de datos de las muestras -------------------
# -------------------------------------------------------------------

# --------------------- Muestras Puras (100%) -----------------------

# ----------------------- Muestras (100%) ---------------------------

# Base de datos para el maíz
maiz_db = [195.0, 1003.0, 732.0, 1438.0, 2079.0, 1631.0, 1242.0, 763.0, 2926.0, 194.0]
poroto_db = [147.0, 742.0, 606.0, 1177.0, 1517.0, 1086.0, 847.0, 577.0, 2085.0, 139.0]
trigo_db = [139.0, 742.0, 592.0, 1113.0, 1387.0, 964.0, 764.0, 530.0, 2001.0, 128.0]

# Diccionario con las muestras puras
muestraspuras_dic = {

        # "luz blanca": luzblanca_db,
        "trigo": trigo_db,
        "maiz": maiz_db,
        "poroto": poroto_db
}

# -------------------------------------------------------------------
# ----------------------- Definición de funciones -------------------
# -------------------------------------------------------------------

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

def mostrar_datos():
    # print("------ Datos de la muestra ------")

    # print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
    # print("F2 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
    # print("F3 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
    # print("F4 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
    # print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
    # print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
    # print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
    # print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
    # print("Clear              %s" % bar_graph(sensor.channel_clear))
    # print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))

    # print("------------------------------------------")

    datos = datos_sensor()
    # promedio_datos_medida(datos)
    hora_santiago = datetime.datetime.now(zona_santiago)
    datos_str = ",".join(map(str, datos))
    foto_id = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
    guardar_datos(datos_str, foto_id, hora_santiago)
    return datos

def promedio_datos_medida(*filas):
    # Obtener el número de filas y el número de columnas
    num_filas = len(filas)
    num_columnas = len(filas[0])

    # Inicializar la matriz de datos
    datos_medida = [[0] * num_columnas for _ in range(num_filas)]

    # Llenar la matriz de datos con las filas proporcionadas
    for i in range(num_filas):
        for j in range(num_columnas):
            # Eliminar corchetes y asteriscos antes de convertir a entero
            valor = filas[i][j].replace("[", "").replace("]", "").replace("*", "").strip()
            datos_medida[i][j] = int(valor)
    
    # Calcular los promedios de cada columna
        promedios_columnas = [sum(columna) / len(columna) for columna in zip(*datos_medida)]

    return promedios_columnas
def distancia_euclidiana(vector_db, vector_medido):
    if len(vector_db) != len(vector_medido):
        raise ValueError("Los vectores deben tener la misma longitud")
    
    suma_cuadrados = sum((x - y) ** 2 for x, y in zip(vector_db, vector_medido))
    distancia = math.sqrt(suma_cuadrados)
    return distancia

def normalizar_vector(vector):
    vector_np = np.array(vector)
    magnitud = np.linalg.norm(vector_np)
    if magnitud == 0:
        return vector_np  # Evitar división por cero
    return vector_np / magnitud

def estimacion_grano(vector_db, vector_medida):
    hora_santiago = datetime.datetime.now(zona_santiago)
    distancias = {}

    # Normalizar el vector de medida
    vector_medida_normalizado = normalizar_vector(vector_medida)
    print(f"Vector Medida Normalizado: {vector_medida_normalizado}")
    
    for grano, vector_referencia in vector_db.items():
        # Normalizar el vector de referencia
        vector_referencia_normalizado = normalizar_vector(vector_referencia)
        #print(f"Vector de {grano} Normalizado: {vector_referencia_normalizado}")

        distancia = distancia_euclidiana(vector_referencia_normalizado, vector_medida_normalizado)
        distancias[grano] = distancia
        print(f"Distancia euclidiana para {grano}: {distancia}")
    
    grano_identificado = min(distancias, key=distancias.get)
    distancia_minima = distancias[grano_identificado]

    if distancia_minima < threshold:
        print(grano_identificado.capitalize())

    else:
        print("Grano desconocido")

def ejecutar_estimacion_grano(vector_medida):
    estimacion_grano(muestraspuras_dic, vector_medida)

def guardar_datos(datos, foto_id, hora_santiago):

    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")
    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada")
    foto_id = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

    datos = datos.split(",")
    # datos.append("")
    datos.append(foto_id)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    #with open(f"/home/pi/SpeGDet/Tests/DataProto2/data_proto2{hora_santiago.strftime('%H%M%S_%d%m%Y')}.csv", mode='a', newline='') as archivo_csv:
    
    with open(f"/home/pi/SpeGDet/Tests/DataProto2/DataEmpty/DataTestEmpty/data_proto2.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)

def tomar_foto():
    try:
        picam2.start()    
        hora_santiago = datetime.datetime.now(zona_santiago)
        #nombre_foto = f"/home/pi/SpeGDet/Tests/DataProto2/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        nombre_foto = f"/home/pi/SpeGDet/Tests/DataProto2/DataEmpty/DataTestEmpty/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
        
        picam2.capture_file(nombre_foto)
        time.sleep(2)

        with open(nombre_foto, "rb") as f:
            data = f.read()
            print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {nombre_foto} guardada")        
        
        # Guardar información de la foto en el archivo CSV
        #foto_id = f"foto_{fecha_hora_actual}.jpg"
        # guardar_datos("", foto_id, hora_santiago)

    except Exception as e:
        print("Error al tomar la foto")

def main():
    
    print("Tomando datos de Poroto")

    # Definición del vector de datos totales de la medida
    datos_medida_final = []

    hora_santiago = datetime.datetime.now(zona_santiago)

    # Comienza recopilando los datos de la muestra
    led_red.on()
    time.sleep(0.2)
    led_red.off()
    led_green.on()
    time.sleep(0.2)
    led_green.off()
    led_yellow.on()
    time.sleep(0.2)
    led_yellow.off()
    led_blue.on()
    time.sleep(0.2)
    led_blue.off()

    # Rutina para tomar datos y foto
    # Toma los datos e inmediatamente la foto

    while True:
            command = input("Ingrese comando (m para medir, q para salir): ")
            
            if command.lower() == 'm':
                for _ in range(meassurement):
                    time.sleep(1)
                    led_array.on()
                    led_red.on()
                    led_blue.on()
                    led_green.on()
                    led_yellow.on()
                    time.sleep(1)
                    led_red.off()
                    led_blue.off()
                    led_green.off()
                    led_yellow.off()
                    #sensor.led_current = 30
                    datos_medida_final.append(mostrar_datos())
                
                tomar_foto()
                led_array.off()

                print("Medida tomada:", datos_medida_final[-1:])
                # Promediar las columnas de los datos totales
                resultados = promedio_datos_medida(*datos_medida_final)
                print("Promedio de cada columna:", resultados)

                ejecutar_estimacion_grano(resultados)
            
            elif command.lower() == 'q':
                print("Saliendo del programa...")
                break
            
            else:
                print("Comando no reconocido. Intente nuevamente.")

    # # Ejecutar mostrar_datos varias veces para agregar datos a la matriz
    # for _ in range(meassurement):
    #     led_array.on()
    #     sensor.led_current = 30
    #     #sensor.led = True
    #     datos_medida_final.append(mostrar_datos())
    
    # tomar_foto()
    # #sensor.led = False
    # led_array.off()

    # # promedio las columnas de los datos totales
    # resultados = promedio_datos_medida(*datos_medida_final)
    # print("Promedio de cada columna:", resultados)

    # ejecutar_estimacion_grano(resultados)

if __name__ == "__main__":
    main()