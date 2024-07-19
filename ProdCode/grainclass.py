import numpy as np
import pandas as pd
import pickle
import re
import time

# Cargar los modelos y centroides
with open('rf_model.pkl', 'rb') as file:
    rf_model = pickle.load(file)

with open('lr_model.pkl', 'rb') as file:
    lr_model = pickle.load(file)

with open('centroids.pkl', 'rb') as file:
    centroids = pickle.load(file)

with open('scaler.pkl', 'rb') as file:
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
def predict_grain_from_csv(csv_file_path):
    # Leer el archivo CSV
    df = pd.read_csv(csv_file_path, header=None, delimiter=',')
    
    # Mostrar la última fila del archivo CSV para depuración
    last_row = df.iloc[-1].values
    #print("Última fila del archivo CSV:", last_row)
    
    # Obtener el último vector, ignorar la primera columna (fecha y hora) y la última columna (nombre del archivo)
    last_vector_str = last_row[1:-1]  # Asegúrate de que estas columnas son las correctas

    # Extraer y convertir a valores numéricos
    last_vector = extract_numeric_values(last_vector_str)
    print("Último vector del archivo CSV:", last_vector)
    
    if not last_vector:
        print("No se encontraron valores numéricos en el vector.")
        return

    # Realizar la predicción
    vector_normalized = normalizar_vector(last_vector)
    #print("Vector normalizado:", vector_normalized)
    
    # Predicción usando la distancia euclidiana
    start_time = time.time()
    class_euclidean = classify_euclidean(vector_normalized, centroids)
    end_time = time.time()
    print(f"Tiempo de predicción usando distancia euclidiana: {end_time - start_time:.4f} segundos")
    print("Predicción usando distancia euclidiana:", class_euclidean)
    
    # Predicción usando Logistic Regression
    predicted_class_lr, proba_lr = predict_lr(vector_normalized)
    print("Predicción usando Logistic Regression:", predicted_class_lr)
    print(f"Probabilidades de pertenencia a cada clase (Logistic Regression): \nMaiz: {proba_lr[0]},\nTrigo: {proba_lr[1]},\nPoroto: {proba_lr[2]},\nNada: {proba_lr[3]} ")
    
    # Predicción usando Random Forest
    predicted_class_rf = predict_rf(vector_normalized)
    print("Predicción usando Random Forest:", predicted_class_rf)

# Ruta del archivo CSV
csv_file_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv"
predict_grain_from_csv(csv_file_path)
