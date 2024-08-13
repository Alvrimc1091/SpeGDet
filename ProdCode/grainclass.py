import numpy as np
import pandas as pd
import pickle
import re
import time
import datetime
import zoneinfo

import os
import sys
import time
import csv
from led_functions import encender_led, secuencia_led_inicializacion, blink_leds, led_blue, led_red, led_yellow, led_green

# Importar la función main de rpisensor
from rpisensor import main as rpisensor_main

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

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

def obtener_ultima_fila(csv_file_path):
    """Obtiene la última fila del archivo CSV y extrae los datos necesarios."""
    df = pd.read_csv(csv_file_path, header=None, delimiter=',')
    last_row = df.iloc[-1]  # Obtener la última fila como una serie
    fecha_hora = last_row[0]
    datos_sensor = last_row[1:-1].apply(lambda x: x.strip()).tolist()  # Limpiar espacios en blanco
    foto_id = last_row.iloc[-1]  # Obtener la última columna usando iloc
    datos_sensor_str = ','.join(datos_sensor)  # Convertir a cadena
    return fecha_hora, datos_sensor_str, foto_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rf_model_path = os.path.join(BASE_DIR, 'rf_model.pkl')
lr_model_path = os.path.join(BASE_DIR, 'lr_model.pkl')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
centroids_path = os.path.join(BASE_DIR, 'centroids.pkl')

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
    print(lr_model.classes_)
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
def predict_grain_from_csv(csv_file_path):
    
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
    print("Último vector del archivo CSV:", last_vector)
    
    if not last_vector:
        print("No se encontraron valores numéricos en el vector.")
        return None

    # Realizar la predicción
    vector_normalized = normalizar_vector(last_vector)
    print("Vector normalizado:", vector_normalized)
    
    # Predicción usando la distancia euclidiana
    class_euclidean = classify_euclidean(vector_normalized, centroids)
    predictions['euclidean'] = {'predicted_class': class_euclidean}
    print("Predicción usando distancia euclidiana:", class_euclidean)
    
    # Predicción usando Logistic Regression
    predicted_class_lr, proba_lr = predict_lr(vector_normalized)
    predictions['logistic_regression'] = {'predicted_class': predicted_class_lr, 'probabilities': proba_lr}
    print("Predicción usando Logistic Regression:", predicted_class_lr)
    print(f"Probabilidades de pertenencia a cada clase (Logistic Regression): \nMaiz: {proba_lr[1]},\nTrigo: {proba_lr[3]},\nPoroto: {proba_lr[2]},\nNada: {proba_lr[0]} ")
    
    # Predicción usando Random Forest
    predicted_class_rf = predict_rf(vector_normalized)
    predictions['random_forest'] = {'predicted_class': predicted_class_rf}
    print("Predicción usando Random Forest:", predicted_class_rf)
    
    # Retornar todas las predicciones
    return {
        'logistic_regression': {
            'predicted_class': predicted_class_lr,
            'probabilities': proba_lr
        },
        'random_forest': predicted_class_rf,
        'euclidean_distance': class_euclidean
    }

def main():
    # Ejecutar la función main de rpisensor.py
    timevar = 0.2
    times = 2
    secuencia_led_inicializacion(timevar)
    time.sleep(1)

    while True:

        blink_leds(times)
        time.sleep(1)
        rpisensor_main()       

        # Obtener la última fila del archivo CSV para usar los mismos datos y hora
        fecha_hora, datos, foto_id = obtener_ultima_fila(csv_file_path)
        
        # Realizar la predicción
        predictions = predict_grain_from_csv(csv_file_path)

        # Manejar la predicción encendiendo el LED adecuado
        manejar_prediccion(predictions)
        
        # Guardar los datos y las predicciones en el nuevo archivo CSV
        guardar_predicciones(fecha_hora, datos, foto_id, predictions)

        time.sleep(5)

if __name__ == "__main__":
    main()

# Ruta del archivo CSV
# csv_file_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv"
# predictions = predict_grain_from_csv(csv_file_path)

# def manejar_prediccion(prediccion):
#     """Maneja la predicción encendiendo el LED correspondiente."""
#     if predictions['logistic_regression']['predicted_class'] == 'poroto':
#         encender_led(led_blue)
#         print('poroto')

#     elif predictions['logistic_regression']['predicted_class'] == 'maiz':
#         encender_led(led_yellow)
#         print('maiz')

#     elif predictions['logistic_regression']['predicted_class'] == 'trigo':
#         encender_led(led_green)
#         print('trigo')
#     else:
#         encender_led(led_red)  # Alerta para casos no reconocidos

# manejar_prediccion(predictions) 
#print("Todas las predicciones:", predictions['euclidean']['predicted_class'])
