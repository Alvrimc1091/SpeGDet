# Script para tomar datos de la muestra
import csv
import socket
import math
import threading
import os
import board
import time
import datetime
import zoneinfo
import pickle
import re
import numpy as np
import pandas as pd
from gpiozero import LED
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

import logging
import socket
import asyncio
import subprocess
import os
import pandas as pd
from pathlib import Path
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Definición del arreglo de LEDs
led_array = LED(17) # LEDs de iluminación para el sensor

led_red = LED(5) # Rojo -> Alerta
led_green = LED(6) # Verde -> Trigo
led_blue = LED(22) # Azul -> Poroto
led_yellow = LED(27) # Amarillo -> Maíz


# Configuración inicial de la cámara
picam2 = Picamera2()
# camera_config = picam2.create_preview_configuration() 
# picam2.configure(camera_config) 
# picam2.start_preview(Preview.NULL)

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

def guardar_datos(datos, foto_id, hora_santiago):

    # print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")
    # print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada")
    foto_id = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

    datos = datos.split(",")
    # datos.append("")
    datos.append(foto_id)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    #with open(f"/home/pi/SpeGDet/Tests/DataProto2/data_proto2{hora_santiago.strftime('%H%M%S_%d%m%Y')}.csv", mode='a', newline='') as archivo_csv:
    
    with open(f"/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)

def tomar_foto():
    try:
        print("tomar_foto: iniciando camara")
        picam2.start()
        print("tomar_foto: camara iniciada")
        hora_santiago = datetime.datetime.now(zona_santiago)
        nombre_foto = f"/home/pi/SpeGDet/DataMeassures/PhotoSensor/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        
        print("tomar_foto: capturando foto")
        picam2.capture_file(nombre_foto)
        print("tomar_foto: foto capturada")
        print("tomar_foto: cerrando picam")
        # picam2.close()
        print("tomar_foto: picamcerrada")

        # Devuelve el nombre del archivo para su uso posterior

    except Exception as e:
        print("Error al tomar la foto")

# Definir la ruta del archivo CSV
csv_file_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv"

predicciones_csv_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/predicciones.csv"

def guardar_predicciones(fecha_hora, datos, foto_id, predictions):
    """Guarda las predicciones en el archivo CSV con la fecha y hora correspondientes."""
    with open("/home/pi/SpeGDet/DataMeassures/DataSensor/predicciones.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([
            fecha_hora,
            datos,
            foto_id,
            predictions['euclidean_distance'],
            predictions['random_forest'],
            predictions['logistic_regression']['predicted_class']
        ])

async def manejar_prediccion(predictions):

    """Maneja la predicción encendiendo el LED correspondiente."""

    if predictions['logistic_regression']['predicted_class'] == 'poroto':
        encender_led(led_blue)
        #print('poroto')

    elif predictions['logistic_regression']['predicted_class'] == 'maiz':
        encender_led(led_yellow)
        #print('maiz')

    elif predictions['logistic_regression']['predicted_class'] == 'trigo':
        encender_led(led_green)
        #print('trigo')
    else:
        encender_led(led_blue)
        encender_led(led_yellow)
        encender_led(led_green)
        encender_led(led_red)  # Alerta para casos no reconocidos

def obtener_ultima_fila(csv_file_path):
    """Obtiene la última fila del archivo CSV y extrae los datos necesarios."""
    df = pd.read_csv(csv_file_path, header=None, delimiter=',')
    last_row = df.iloc[-1]  # Obtener la última fila como una serie
    fecha_hora = last_row[0]
    datos_sensor = last_row[1:-1].apply(lambda x: x.strip()).tolist()  # Limpiar espacios en blanco
    foto_id = last_row.iloc[-1]  # Obtener la última columna usando iloc
    datos_sensor_str = ','.join(datos_sensor)  # Convertir a cadena
    return fecha_hora, datos_sensor_str, foto_id

rf_model_path = 'rf_model.pkl'
lr_model_path = 'lr_model.pkl'
scaler_path = 'scaler.pkl'
centroids_path = 'centroids.pkl'

# Cargar los modelos y centroides
with open(rf_model_path, 'rb') as file:
    rf_model = pickle.load(file)

with open(lr_model_path, 'rb') as file:
    lr_model = pickle.load(file)

with open(centroids_path, 'rb') as file:
    centroids = pickle.load(file)

with open(scaler_path, 'rb') as file:
    scaler = pickle.load(file)

# Función para normalizar un vector
def normalizar_vector(vector):
    vector_np = np.array(vector)
    if vector_np.size == 0:
        return vector_np
    magnitud = np.linalg.norm(vector_np)
    if magnitud == 0:
        return vector_np  # Evitar división por cero
    return vector_np / magnitud

# Calcular la distancia euclidiana entre dos vectores
def euclidean_distance(vector1, vector2):
    if vector1.size == 0 or vector2.size == 0:
        return float('inf')  # Retornar infinito si uno de los vectores está vacío
    return np.linalg.norm(vector1 - vector2)

# Clasificación basada en la distancia euclidiana
def classify_euclidean(vector, centroids):
    if vector.size == 0:
        return None
    distances = {label: euclidean_distance(vector, centroid) for label, centroid in centroids.items()}
    return min(distances, key=distances.get)

# Función para realizar la predicción con Logistic Regression
def predict_lr(vector):
    start_time = time.time()  # Comenzar temporizador
    vector_normalized = normalizar_vector(vector)
    vector_scaled = scaler.transform([vector_normalized])
    proba = lr_model.predict_proba(vector_scaled)
    predicted_class = lr_model.predict(vector_scaled)[0]
    end_time = time.time()  # Detener temporizador
    print(f"Tiempo de predicción con Logistic Regression: {end_time - start_time:.4f} segundos")
    return predicted_class, proba[0]

# Función para realizar la predicción con Random Forest
def predict_rf(vector):
    start_time = time.time()  # Comenzar temporizador
    vector_normalized = normalizar_vector(vector)
    vector_scaled = scaler.transform([vector_normalized])
    predicted_class = rf_model.predict(vector_scaled)[0]
    end_time = time.time()  # Detener temporizador
    print(f"Tiempo de predicción con Random Forest: {end_time - start_time:.4f} segundos")
    return predicted_class

# Función para extraer valores numéricos de una fila del CSV
def extract_numeric_values(row):
    # Utilizar expresión regular para encontrar números entre corchetes
    pattern = re.compile(r'\[ *(\d+)\]')
    numeric_values = pattern.findall(' '.join(row))  # Unir todos los elementos en una cadena y buscar números
    return [int(value) for value in numeric_values]

# Función principal para predecir el grano desde el archivo CSV
async def predict_grain_from_csv(csv_file_path):
    
    # Diccionario para guardar las predicciones
    predictions = {'euclidean': None, 'logistic_regression': None, 'random_forest': None}

    # Leer el archivo CSV
    df = pd.read_csv(csv_file_path, header=None, delimiter=',')
    
    # Mostrar la última fila del archivo CSV para depuración
    last_row = df.iloc[-1].values
    
    # Obtener el último vector, ignorar la primera columna (fecha y hora) y la última columna (nombre del archivo)
    last_vector_str = last_row[1:-1]  # Asegúrate de que estas columnas son las correctas

    # Extraer y convertir a valores numéricos
    last_vector = extract_numeric_values(last_vector_str)
    # await bot.send_message(chat_id=CHAT_ID, text=f"Último vector del archivo CSV: {last_vector}")
    
    if not last_vector:
        await bot.send_message(chat_id=CHAT_ID, text="No se encontraron valores numéricos en el vector.")
        return None

    # Realizar la predicción
    vector_normalized = normalizar_vector(last_vector)
    # await bot.send_message(chat_id=CHAT_ID, text=f"Vector normalizado: {vector_normalized}")

    await bot.send_message(chat_id=CHAT_ID, text=f"A continuación se muestran los resultados de la medición:")
    
    # Predicción usando la distancia euclidiana
    class_euclidean = classify_euclidean(vector_normalized, centroids)
    predictions['euclidean'] = {'predicted_class': class_euclidean}
    # await bot.send_message(chat_id=CHAT_ID, text=f"Predicción usando distancia euclidiana: {class_euclidean}")
    
    # Predicción usando Logistic Regression (Predicción 1)
    predicted_class_lr, proba_lr = predict_lr(vector_normalized)
    predictions['logistic_regression'] = {'predicted_class': predicted_class_lr, 'probabilities': proba_lr}
    await bot.send_message(chat_id=CHAT_ID, text=f"Predicción 1: {predicted_class_lr}")
    await bot.send_message(chat_id=CHAT_ID, text=f"Probabilidades de pertenencia a cada clase: \nMaíz: {proba_lr[0]} %,\nTrigo: {proba_lr[1]} %,\nPoroto: {proba_lr[2]}%,\nVacío: {proba_lr[3]}%")
    
    # Predicción usando Random Forest (Predicción 2)
    predicted_class_rf = predict_rf(vector_normalized)
    predictions['random_forest'] = {'predicted_class': predicted_class_rf}
    await bot.send_message(chat_id=CHAT_ID, text=f"Predicción 2: {predicted_class_rf}")
    
    # Retornar todas las predicciones
    return {
        'logistic_regression': {
            'predicted_class': predicted_class_lr,
            'probabilities': proba_lr
        },
        'random_forest': predicted_class_rf,
        'euclidean_distance': class_euclidean
    }


# Configuración del token del bot de Telegram
TOKEN = "7327013745:AAH8hl6XfNlHoZcsoNtAlC9RU_wM6azxWiE"

# ID del chat donde enviarás la IP (puedes obtenerlo usando el bot de Telegram @userinfobot)
CHAT_ID = "5129990683"

bot = Bot(token=TOKEN)

# Directorios
PHOTO_DIR = "/home/pi/SpeGDet/DataMeassures/PhotoSensor"
CSV_FILE = "/home/pi/SpeGDet/DataMeassures/DataSensor/predicciones.csv"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

async def get_local_ip():
    """
    Obtiene la dirección IP local de la Raspberry Pi.
    """
    try:
        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Conectar a un servidor externo (Google DNS)
        ip_address = sock.getsockname()[0]  # Obtener la dirección IP asignada a la interfaz de red
        sock.close()
        return ip_address
    except Exception as e:
        logger.error(f"Error al obtener la dirección IP: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /start.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy tu bot de Raspberry Pi. Usa /ip para obtener la IP, /l para ejecutar el script led.py, /graindetector para ejecutar graindetector.py, /graindetector2 para ejecutar graindetector2.py y /getphoto para obtener la última foto.")

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /ip.
    """
    ip_address = await get_local_ip()
    if ip_address:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"La IP de esta Raspberry Pi es: {ip_address}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No se pudo recuperar la dirección IP.")

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /getphoto que envía la última foto y la información asociada al chat de Telegram.
    """
    try:
        # Obtener la última foto en términos de fecha y hora
        files = list(Path(PHOTO_DIR).glob('foto_*.jpg'))
        if files:
            latest_photo = max(files, key=os.path.getctime)
            
            # Leer el archivo CSV para encontrar la predicción asociada a la última foto
            df = pd.read_csv(CSV_FILE, header=None, names=["fecha", "valores", "foto", "dist_euc", "rf", "log_reg"], sep=',')
            logger.info(f"DataFrame cargado:\n{df.head()}")  # Verifica los primeros registros del DataFrame
            
            latest_photo_name = latest_photo.name
            logger.info(f"Última foto detectada: {latest_photo_name}")
            
            # Verificar nombres de fotos en el DataFrame
            fotos_en_df = df['foto'].unique()
            logger.info(f"Nombres de fotos en el DataFrame: {fotos_en_df}")
            
            # Buscar la fila correspondiente a la última foto
            pred_info = df[df["foto"].str.strip() == latest_photo_name]
            
            if not pred_info.empty:
                pred_info = pred_info.iloc[0]
                
                # Crear el mensaje de texto con la información de la predicción
                mensaje = (
                    f"Fecha: {pred_info['fecha']},\n"
                    f"Foto: {latest_photo_name}\n"
                    f"Predicción por Distancia Euclidiana: {pred_info['dist_euc']}\n"
                    f"Predicción por Random Forest: {pred_info['rf']}\n"
                    f"Predicción por Logistic Regression: {pred_info['log_reg']}"
                )
                
                # Enviar la foto y la información al chat de Telegram
                with open(latest_photo, 'rb') as photo_file:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)
                
                logger.info(f"Última foto y predicción enviada: {latest_photo_name}")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontró información de predicción para la foto.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontraron fotos en el directorio.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al intentar enviar la foto y la predicción: {e}")

# Función para obtener el nombre del archivo de la última fila del CSV
def obtener_nombre_foto_ultimo_csv(csv_file_path):
    df = pd.read_csv(csv_file_path, header=None)
    # Asumiendo que el nombre del archivo está en la última columna
    return df.iloc[-1, -1]  # La última fila, última columna

async def mostrar_foto(nombre_foto):
    try:
        # Extraer la parte del nombre del archivo que contiene la fecha y hora
        base_name = os.path.basename(nombre_foto)
        time_str = base_name.split('_')[1].split('.')[0]  # Formato HHMMSS
        date_str = base_name.split('_')[2].split('.')[0]  # Formato DDMMYYYY

        # Convertir el string de fecha y hora en un objeto datetime
        hora_santiago = datetime.datetime.strptime(f"{date_str}{time_str}", '%d%m%Y%H%M%S')

        # Generar las tres posibles horas
        horas_posibles = [
            hora_santiago - datetime.timedelta(seconds=1),
            hora_santiago,
            hora_santiago + datetime.timedelta(seconds=1)
        ]

        # Buscar los archivos correspondientes a cada hora posible
        archivo_encontrado = None
        for hora in horas_posibles:
            nuevo_nombre_foto = f"/home/pi/SpeGDet/DataMeassures/PhotoSensor/foto_{hora.strftime('%H%M%S_%d%m%Y')}.jpg"
            if os.path.exists(nuevo_nombre_foto):
                archivo_encontrado = nuevo_nombre_foto
                break

        # Enviar la foto si se encontró un archivo existente
        if archivo_encontrado:
            with open(archivo_encontrado, "rb") as f:
                data = f.read()
                await bot.send_message(chat_id=CHAT_ID, text="Foto tomada, el resultado se muestra a continuación.")
                await bot.send_photo(chat_id=CHAT_ID, photo=data)
                print(f"Foto enviada: {archivo_encontrado}")
        else:
            print(f"No se encontró ningún archivo con los nombres posibles.")

    except Exception as e:
        print(f"Error al mostrar la foto: {e}")

async def main():

  
    # Ejecutar la función main de rpisensor.py
    timevar = 0.2
    times = 3

    secuencia_led_inicializacion(timevar)

    # main de rpisensor:    
    
    # Definición del vector de datos totales de la medida
    datos_medida_final = []

    hora_santiago = datetime.datetime.now(zona_santiago)
    # Comienza recopilando los datos de la muestra

    # Rutina para tomar datos y foto
    # Toma los datos e inmediatamente la foto
    #print("Cámara Inicializada")
    await bot.send_message(chat_id=CHAT_ID, text="Iniciando toma de datos. Por favor no desconecte el sensor.")

    #print("Iniciando toma de foto y datos de la muestra")
    # await bot.send_message(chat_id=CHAT_ID, text="Iniciando toma de foto y datos de la muestra")
    led_array.on()
    time.sleep(1)
    
    #for _ in range(meassurement):
        #sensor.led_current = 30
    
    print("Tomando datos")
    datos_medida_final.append(mostrar_datos())
    #await bot.send_message(chat_id=CHAT_ID, text=f"Medida tomada: {datos_medida_final.append(mostrar_datos())}")

    print("Datos tomados")
    
    # picam2.start()
    tomar_foto()
    # picam2.close()

    # Obtener el nombre del archivo de la última fila del CSV
    nombre_foto = obtener_nombre_foto_ultimo_csv(csv_file_path)
    print(f"Nombre de la foto desde CSV: {nombre_foto}")

    # Mostrar la foto en el bot
    await mostrar_foto(f"/home/pi/SpeGDet/DataMeassures/PhotoSensor/{nombre_foto}")

    led_array.off()
    print("Arreglo de leds apagados")

    print("Mostrando datos a continuación")
    print("Medida tomada:", datos_medida_final[-1:])
    # Promediar las columnas de los datos totales
    resultados = promedio_datos_medida(*datos_medida_final)
    print("Promedio de cada columna:", resultados)

    blink_leds(times)
    print("Parpadeo completo")
    
    # Ejecución main de grainclass
    print("Revisando datos de muestra que fueron tomados")
    # Obtener la última fila del archivo CSV para usar los mismos datos y hora
    fecha_hora, datos, foto_id = obtener_ultima_fila(csv_file_path)
    print("Datos de la última muestra encontrados")

    # Realizar la predicción
    print("Predicción completa, mostrando resultados:")
    predictions = await predict_grain_from_csv(csv_file_path)
    print("Predicción completa")

    await manejar_prediccion(predictions)

    # Manejar la predicción encendiendo el LED adecuado
    print("Encendiendo leds en base a predicción")
    manejar_prediccion(predictions)
    print("Manejo de leds completa")
    
    print("Guardando datos de predicción")
    # Guardar los datos y las predicciones en el nuevo archivo CSV
    guardar_predicciones(fecha_hora, datos, foto_id, predictions)
    print("Datos de predicción guardados")

    # # Ejecutar get_photo al final
    # await get_photo()

async def iniciar_bot():

    # Configurar el bot
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ip", ip))
    application.add_handler(CommandHandler("getphoto", get_photo))

    # Ejecutar el bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # # Rutina de inicialización: Mensajes de bienvenida en el chat de Telegram
    # await bot.send_message(chat_id=CHAT_ID, text="--------------------------------------------")
    # await bot.send_message(chat_id=CHAT_ID, text="------------ NOMBRE PROYECTO V1 ------------")
    # await bot.send_message(chat_id=CHAT_ID, text="--------------------------------------------")
    # await bot.send_message(chat_id=CHAT_ID, text="Bienvenido/a al Detector Espectral de Granos")

async def main_loop():
    while True:
        try:
            await main()
        except Exception as e:
            print(f"Error en la ejecución: {e}")
        await asyncio.sleep(20)  # Espera 15 segundos antes de la próxima ejecución

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(iniciar_bot())
    loop.run_until_complete(main_loop())