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

# print(sensor.atime)
# print(sensor.astep)
# print(sensor.gain) #= 512

# Sensor ATIME (Por defecto es 100)
sensor.atime = 29

# Sensor ASTEP (Por defecto es 999)
sensor.astep = 599

# Con ATIME = 29 y ASTEP = 599 se tiene t_int igual a 50ms
# Con ATIME = 100 y ASTEP = 999 se tiene t_int igual a 280ms

# Sensor GAIN (Por defecto es 8 (128))
sensor.gain = 10

# Definición de contador total de muestras
meassurement = 1

# Definición del threshold
threshold = 0.2
threshold_proto2 = 0.5

# sensor.led = 

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

# Base de datos para la luz blanca
luzblanca_db = [770.8, 6034.7, 2179.6, 3800.3, 4651.4, 3841.8, 2659.8, 1182.7, 1, 1]
#, 13999.6, 469.3]

# Base de datos para el trigo
trigo_db =  [44.24, 373.36, 174.68, 291.68, 472.0, 472.32, 352.6, 214.76, 1055.92, 57.04]
trigo_normalizado_db = [0.03134921, 0.26456922, 0.12378121, 0.20668939, 0.33446719, 0.33469395, 0.24985833, 0.15218257, 0.74824279, 0.04041951]
trigo_proto2_db = [61.7, 462.35, 170.1, 329.8, 384.55, 339.9, 231.55, 101.15, 339.25, 15.95]
trigo_proto2_normalizado_db = [0.03134921, 0.26456922, 0.12378121, 0.20668939, 0.33446719, 0.33469395, 0.24985833, 0.15218257, 0.74824279, 0.04041951]
#[178.71428571428572, 1705.0, 831.3333333333334, 1354.5714285714287, 2192.3333333333335, 2167.4761904761904, 1631.7619047619048, 1038.4761904761904, 1, 1]
#[159.2, 1328.8, 662.0, 1208.1, 2060.0, 2075.8, 1581.8, 1065.6] # Promedio muestras movimiento y cristal

# Promedio datos estáticos = [159.2, 1328.8, 662.0, 1208.1, 2060.0, 2075.8, 1581.8, 1065.6]
# Promedio Total = [275.68, 2830.8, 1196.76, 2126.4, 3114.0, 2992.44, 2073.2, 1286.24]


# Old Data
# -------------------------------------------------------------------
#[154.6, 1346.9, 664.7, 1306.3, 2091.5, 2101.7, 1581.5, 973.2]#, 4204.8, 241.1]
#[152.0, 1306.7, 653.1, 1274.8, 2014.1, 2096.3, 1597.7, 978.0, 5074.0, 281.6]
# -------------------------------------------------------------------

# Base de datos para el maíz
maiz_db = [54.65384615384615, 405.6923076923077, 208.6153846153846, 366.34615384615387, 716.0, 730.6923076923077, 532.0769230769231, 316.1923076923077, 1542.7692307692307, 89.42307692307692]

maiz_proto1_db = [54.65384615384615, 405.6923076923077, 208.6153846153846, 366.34615384615387, 716.0, 730.6923076923077, 532.0769230769231, 316.1923076923077, 1542.7692307692307, 89.42307692307692]
maiz_normalizado_db = [0.02678632, 0.19883325, 0.10224418, 0.17954937, 0.35091769, 0.35811852, 0.26077543, 0.15496854, 0.75612433, 0.04382701]
maiz_proto2_db = [44.55, 356.45, 141.5, 270.0, 334.2, 306.1, 213.05, 93.5, 431.35, 17.7] # maiz_proto2
maiz_proto2_normalizado_db = [0.03134921, 0.26456922, 0.12378121, 0.20668939, 0.33446719, 0.33469395, 0.24985833, 0.15218257, 0.74824279, 0.04041951]

#[245.0, 2041.85, 1036.85, 1781.6, 3382.75, 3404.25, 2522.4, 1536.85, 1, 1]
#[237.0, 1701.1, 904.8, 1692.9, 3570.5, 3564.4, 2690.7, 1725.4] # Promedio muestras movimiento y cristal

# Promedio estático =  [237.0, 1701.1, 904.8, 1692.9, 3570.5, 3564.4, 2690.7, 1725.4]
# Promedio Maiz Total = [366.916666, 2734.458333, 1263.291666, 2405.625, 4256.416666, 4093.833333, 2992.75, 1759.791666]

# Old Data
#[227.0, 1552.3, 790.3, 1812.3, 3524.2, 3653.9, 2695.7, 1479.4]#, 6352.3, 391.4]
#[260.0, 2083.1, 1073.0, 2189.6, 4200.4, 4244.7, 3097.0, 1841.8, 9451.1, 533.2]

# Base de datos para la poroto

poroto_db = [40.4, 322.48, 168.4, 288.8, 487.4, 492.76, 364.44, 236.44, 1059.04, 61.32]
poroto_normalizado_db = [0.02848316, 0.22735768, 0.11872685, 0.20361231, 0.34363103, 0.34740998, 0.25694069, 0.16669701, 0.74665369, 0.04323237]
poroto_proto2_db = [50.05555555555556, 395.80555555555554, 153.02777777777777, 288.5833333333333, 340.3611111111111, 303.1111111111111, 208.97222222222223, 92.63888888888889, 370.52777777777777, 15.805555555555555]
poroto_proto2_normalizado_db = [0.03134921, 0.26456922, 0.12378121, 0.20668939, 0.33446719, 0.33469395, 0.24985833, 0.15218257, 0.74824279, 0.04041951]
#[177.8, 1629.6, 830.8, 1427.1, 2325.3, 2318.65, 1727.7, 1135.9, 1, 1]
#[151.1, 1129.2, 652.1, 1184.4, 2179.4, 2155.4, 1684.3, 1206.7] # Promedio en movimiento y cristal 

# Promedio muestras estáticas = [151.1, 1129.2, 652.1, 1184.4, 2179.4, 2155.4, 1684.3, 1206.7]
# Promedio total = [303.538461, 2252.0, 1054.923076, 1984.230769, 3058.846153, 2878.961538, 2148.923076, 1331.538461]


# Old Data
#[146.0, 1044.0, 598.2, 1256.3, 2112.8, 2191.6, 1701.0, 1132.1]#, 4349.1, 270.7]
#[169.3, 1412.0, 754.8, 1525.2, 2449.0, 2579.1, 1958.6, 1315.9, 6339.1, 373.7]

# ------------------- Muestras mezcladas (50/50) --------------------

# # Base de datos para trigo/maiz
# trigomaiz_db = [207.8, 1814.0, 919.4, 1558.1, 2796.0, 2781.85, 2096.25, 1317.2, 1, 1]

# # Base de datos para trigo/poroto
# trigoporoto_db = [176.8, 1646.5, 847.5, 1377.45, 2311.0, 2257.65, 1731.05, 1164.4, 1, 1]

# # Base de datos para maiz/poroto
# maizporoto_db = [208.5, 1799.8, 904.7, 1649.2, 2882.55, 2869.95, 2109.35, 1286.6, 1, 1]

# Diccionario con las muestras puras
muestraspuras_dic = {

        # "luz blanca": luzblanca_db,
        "trigo": trigo_db,
        "maiz": maiz_db,
        "poroto": poroto_db
        # "poroto/maiz": maizporoto_db,
        # "trigo/maiz": trigomaiz_db,
        # "trigo/poroto": trigoporoto_db
}

muestraspuras_proto2_dic = {
    "trigo": trigo_proto2_db,
    "maiz": maiz_proto2_db,
    "poroto": poroto_proto2_db
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
    foto_id = f"foto_up_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
    #guardar_datos(datos_str, foto_id, hora_santiago)
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

def estimacion_grano(vector_db, vector_proto2_db, vector_medida):
    hora_santiago = datetime.datetime.now(zona_santiago)
    distancias = {}
    distancias_proto2 = {}

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
    
    # for grano_proto2, vector_referencia_proto2 in vector_proto2_db.items():
    #     # Normalizar el vector de referencia
    #     vector_referencia_normalizado_proto2 = normalizar_vector(vector_referencia_proto2)
    #     #print(f"Vector de {grano} Normalizado: {vector_referencia_normalizado}")

    #     distancia_proto2 = distancia_euclidiana(vector_referencia_normalizado_proto2, vector_medida_normalizado)
    #     distancias_proto2[grano_proto2] = distancia_proto2
    #     print(f"Distancia euclidiana (Proto 2) para {grano_proto2}: {distancia_proto2}")
    
    grano_identificado = min(distancias, key=distancias.get)
    distancia_minima = distancias[grano_identificado]
    
    # grano_identificado_proto2 = min(distancias_proto2, key=distancias_proto2.get)
    # distancia_minima_proto2 = distancias_proto2[grano_identificado_proto2]

    if distancia_minima < threshold:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string(grano_identificado.capitalize(), 2)
        print(grano_identificado.capitalize())
        time.sleep(2)

    # elif threshold >= 0.1 and not distancia_minima < threshold :
        
    #     if distancia_minima_proto2 < threshold_proto2:
    #         limpiar_pantalla(hora_santiago)
    #         lcd.lcd_display_string(grano_identificado_proto2.capitalize(), 2)
    #         print(grano_identificado_proto2.capitalize())
    #         time.sleep(2)

    #     else:
    #         limpiar_pantalla(hora_santiago)
    #         lcd.lcd_display_string("Desconocido", 2)
    #         print("Grano desconocido")
    #         time.sleep(2)

    else:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string("Desconocido", 2)
        print("Grano desconocido")
        time.sleep(2)

def ejecutar_estimacion_grano(vector_medida):
    estimacion_grano(muestraspuras_dic, muestraspuras_proto2_dic, vector_medida)

def guardar_datos(datos, foto_id, hora_santiago):

    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")
    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada")
    foto_id = f"foto_up_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

    datos = datos.split(",")
    # datos.append("")
    datos.append(foto_id)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    with open(f"/home/pi/SpeGDet/Tests/Data/data_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)

def tomar_foto():
    try:
        picam2.start()    
        hora_santiago = datetime.datetime.now(zona_santiago)
        nombre_foto = f"/home/pi/SpeGDet/Tests/Data/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
        
        #picam2.capture_file(nombre_foto)
        time.sleep(2)

        with open(nombre_foto, "rb") as f:
            data = f.read()
            #print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {nombre_foto} guardada")        
        
        # Guardar información de la foto en el archivo CSV
        #foto_id = f"foto_{fecha_hora_actual}.jpg"
        # guardar_datos("", foto_id, hora_santiago)

    except Exception as e:
        print("Error al tomar la foto")

def limpiar_pantalla(hora_santiago):
    lcd.lcd_clear()
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)

def main():
    
    # Definición del vector de datos totales de la medida
    datos_medida_final = []

    hora_santiago = datetime.datetime.now(zona_santiago)

    # Comienza recopilando los datos de la muestra
    # Imprime un mensaje en pantalla
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Tomando datos", 2)
    time.sleep(1)

    # Rutina para tomar datos y foto
    # Toma los datos e inmediatamente la foto

    # Ejecutar mostrar_datos varias veces para agregar datos a la matriz
    for _ in range(meassurement):
        led_array.on()
        sensor.led_current = 30
        #sensor.led = True
        datos_medida_final.append(mostrar_datos())
    
    tomar_foto()
    sensor.led = False
    led_array.off()

    # Envía mensaje de que los datos fueron guardados
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Datos guardados", 2)
    time.sleep(1)

    # Envía mensaje de que la foto fue guardada
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Foto guardada", 2)
    time.sleep(1)

    # Cierre de la medición
    # Imprime mensaje de finalización de la medición
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Medicion lista", 2)
    time.sleep(1)

    # Procesamiento de la medición
    # Procesa los datos tomados y realiza la estimación
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Procesando datos", 2)
    time.sleep(1)

    # promedior las columnas de los datos totales
    resultados = promedio_datos_medida(*datos_medida_final)
    print("Promedio de cada columna:", resultados)

    ejecutar_estimacion_grano(resultados)

if __name__ == "__main__":
    main()

