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

# Definición de contador total de muestras
meassurement = 10

# Definición del threshold
threshold = 10000

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

# Base de datos para la luz blanca
luzblanca_db = [770.8, 6034.7, 2179.6, 3800.3, 4651.4, 3841.8, 2659.8, 1182.7, 13999.6, 469.3]

# Base de datos para el trigo
trigo_db = [154.6, 1346.9, 664.7, 1306.3, 2091.5, 2101.7, 1581.5, 973.2]#, 4204.8, 241.1]
#[152.0, 1306.7, 653.1, 1274.8, 2014.1, 2096.3, 1597.7, 978.0, 5074.0, 281.6]

# Base de datos para el maíz
maiz_db = [227.0, 1552.3, 790.3, 1812.3, 3524.2, 3653.9, 2695.7, 1479.4]#, 6352.3, 391.4]
#[260.0, 2083.1, 1073.0, 2189.6, 4200.4, 4244.7, 3097.0, 1841.8, 9451.1, 533.2]

# Base de datos para la poroto
poroto_db = [146.0, 1044.0, 598.2, 1256.3, 2112.8, 2191.6, 1701.0, 1132.1]#, 4349.1, 270.7]
#[169.3, 1412.0, 754.8, 1525.2, 2449.0, 2579.1, 1958.6, 1315.9, 6339.1, 373.7]

# Diccionario con las muestras puras
muestraspuras_dic = {

        "trigo": trigo_db,
        "maiz": maiz_db,
        "poroto": poroto_db
}

# ------------------- Muestras mezcladas (50/50) --------------------

# Base de datos para trigo/maiz
trigomaiz_db = []

# Base de datos para trigo/poroto
trigoporoto_db = []

# Base de datos para maiz/poroto
maizporoto_db = []

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
        bar_graph(sensor.channel_680nm)
        # bar_graph(sensor.channel_clear),
        # bar_graph(sensor.channel_nir)
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
    # print("Clear              %s" % bar_graph(sensor.channel_clear))
    # print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))

    print("------------------------------------------")

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

def estimacion_grano(vector_db, vector_medida):
    hora_santiago = datetime.datetime.now(zona_santiago)
    distancias = {}
    
    for grano, vector_referencia in vector_db.items():
        distancia = distancia_euclidiana(vector_referencia, vector_medida)
        distancias[grano] = distancia
        print(f"Distancia euclidiana para {grano}: {distancia}")
    
    grano_identificado = min(distancias, key=distancias.get)
    distancia_minima = distancias[grano_identificado]
    
    if distancia_minima < threshold:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string(grano_identificado.capitalize(), 2)
        print(grano_identificado.capitalize())
        time.sleep(3)
    else:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string("Desconocido", 2)
        print("Grano desconocido")
        time.sleep(3)

def ejecutar_estimacion_grano(vector_medida):
    estimacion_grano(muestraspuras_dic, vector_medida)

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
        
        picam2.capture_file(nombre_foto)
        time.sleep(2)

        with open(nombre_foto, "rb") as f:
            data = f.read()
            #print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {nombre_foto} guardada")        
        
        # Guardar información de la foto en el archivo CSV
        foto_id = f"foto_{fecha_hora_actual}.jpg"
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
    time.sleep(3)

    # Rutina para tomar datos y foto
    # Toma los datos e inmediatamente la foto

    # Ejecutar mostrar_datos varias veces para agregar datos a la matriz
    for _ in range(meassurement):
        led_array.on()
        datos_medida_final.append(mostrar_datos())
    
    tomar_foto()
    led_array.off()

    # Envía mensaje de que los datos fueron guardados
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Datos guardados", 2)
    time.sleep(2)

    # Envía mensaje de que la foto fue guardada
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Foto guardada", 2)
    time.sleep(2)

    # Cierre de la medición
    # Imprime mensaje de finalización de la medición
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Medicion lista", 2)
    time.sleep(2)

    # Procesamiento de la medición
    # Procesa los datos tomados y realiza la estimación
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Procesando datos", 2)
    time.sleep(3)

    # promedior las columnas de los datos totales
    resultados = promedio_datos_medida(*datos_medida_final)
    print("Promedio de cada columna:", resultados)

    ejecutar_estimacion_grano(resultados)

if __name__ == "__main__":
    main()

