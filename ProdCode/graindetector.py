import os
import sys
import time
import csv
import datetime
import zoneinfo
import pandas as pd
from led_functions import encender_led, secuencia_led_inicializacion, blink_leds, led_blue, led_red, led_yellow, led_green

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Asegúrate de que el directorio actual esté en el path para permitir las importaciones
# Establecer el directorio de trabajo en el directorio del script
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar la función main de rpisensor
from rpisensor import main as rpisensor_main

# Importar la función predict_grain_from_csv de grainclass
from grainclass import predict_grain_from_csv

# Definir la ruta del archivo CSV
csv_file_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv"

predicciones_csv_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/predicciones.csv"

def obtener_ultima_fila(csv_file_path):
    """Obtiene la última fila del archivo CSV y extrae los datos necesarios."""
    df = pd.read_csv(csv_file_path, header=None, delimiter=',')
    last_row = df.iloc[-1]  # Obtener la última fila como una serie
    fecha_hora = last_row[0]
    datos_sensor = last_row[1:-1].apply(lambda x: x.strip()).tolist()  # Limpiar espacios en blanco
    foto_id = last_row.iloc[-1]  # Obtener la última columna usando iloc
    datos_sensor_str = ','.join(datos_sensor)  # Convertir a cadena
    return fecha_hora, datos_sensor_str, foto_id

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

def manejar_prediccion(predictions):

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
        encender_led(led_red)  # Alerta para casos no reconocidos

def main():
    # Ejecutar la función main de rpisensor.py
    timevar = 0.2
    times = 3

    secuencia_led_inicializacion(timevar)
    rpisensor_main()
    blink_leds(times)
    
    # Obtener la última fila del archivo CSV para usar los mismos datos y hora
    fecha_hora, datos, foto_id = obtener_ultima_fila(csv_file_path)
    
    # Realizar la predicción
    predictions = predict_grain_from_csv(csv_file_path)
    
    # Manejar la predicción encendiendo el LED adecuado
    manejar_prediccion(predictions)
    
    # Guardar los datos y las predicciones en el nuevo archivo CSV
    guardar_predicciones(fecha_hora, datos, foto_id, predictions)

if __name__ == "__main__":
    main()
