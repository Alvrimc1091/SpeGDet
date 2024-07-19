# Script para guardar los modelos en un archivo con extensión .pkl
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
import pickle
import re
import warnings
from sklearn.exceptions import ConvergenceWarning

# Ignorar advertencias de convergencia
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# Función para normalizar un vector
def normalizar_vector(vector):
    vector_np = np.array(vector)
    magnitud = np.linalg.norm(vector_np)
    if magnitud == 0:
        return vector_np  # Evitar división por cero
    return vector_np / magnitud

# Función para extraer valores numéricos de una fila dada
def extract_numeric_values(row):
    pattern = re.compile(r'\[ *(\d+)\]')
    numeric_values = pattern.findall(row[0])  # Usar solo la primera columna para la extracción
    return [int(value) for value in numeric_values]

# Leer los datos desde archivos CSV
def read_grain_data(file_path, label):
    df = pd.read_csv(file_path, sep='\t', header=None)
    df['label'] = label
    return df

# Definir los archivos CSV y las etiquetas
file_paths = {
    'maiz_pure': "~/SpeGDet/Tests/DataProto2/DataMaiz/DataPureMaiz/data_proto2.csv",
    'maiz_shake': "~/SpeGDet/Tests/DataProto2/DataMaiz/DataShakeMaiz/data_proto2.csv",
    'maiz_cristal': "~/SpeGDet/Tests/DataProto2/DataMaiz/DataCristalMaiz/data_proto2.csv",
    'trigo_pure': "~/SpeGDet/Tests/DataProto2/DataTrigo/DataPureTrigo/data_proto2.csv",
    'trigo_shake': "~/SpeGDet/Tests/DataProto2/DataTrigo/DataShakeTrigo/data_proto2.csv",
    'trigo_cristal': "~/SpeGDet/Tests/DataProto2/DataTrigo/DataCristalTrigo/data_proto2.csv",
    'poroto_pure': "~/SpeGDet/Tests/DataProto2/DataPoroto/DataPurePoroto/data_proto2.csv",
    'poroto_cristal': "~/SpeGDet/Tests/DataProto2/DataPoroto/DataCristalPoroto/data_proto2.csv",
    'poroto_shake': "~/SpeGDet/Tests/DataProto2/DataPoroto/DataShakePoroto/data_proto2.csv",
    'empty_clean': "~/SpeGDet/Tests/DataProto2/DataEmpty/DataCleanEmpty/data_proto2.csv",
    'empty_dirty': "~/SpeGDet/Tests/DataProto2/DataEmpty/DataDirtyEmpty/data_proto2.csv"
}

# Leer y combinar todos los datos de grano
dfs = []
for key, path in file_paths.items():
    label = key.split('_')[0]  # Obtener 'maiz', 'trigo', 'poroto', 'empty' de las claves
    df = read_grain_data(path, label)
    dfs.append(df)

# Combinar todos los dataframes en uno solo
df_combined = pd.concat(dfs, ignore_index=True)

# Función para limpiar y extraer valores numéricos
def clean_and_extract(df):
    df_cleaned = df.apply(lambda row: pd.Series(extract_numeric_values(row)), axis=1)
    return df_cleaned

# Balancear los datos
def balance_data(df):
    max_size = df['label'].value_counts().max()
    lst = [df]
    for class_index, group in df.groupby('label'):
        lst.append(group.sample(max_size - len(group), replace=True))
    df_new = pd.concat(lst)
    return df_new

# Limpiar y extraer valores numéricos para todo el dataset
df_cleaned = clean_and_extract(df_combined)
df_cleaned['label'] = df_combined['label']

# Normalizar cada fila de características
normalized_features = df_cleaned.iloc[:, :-1].apply(lambda row: normalizar_vector(row), axis=1)

# Crear un DataFrame con los datos normalizados
df_normalized = pd.DataFrame(normalized_features.tolist(), index=df_cleaned.index)
df_normalized.columns = df_cleaned.columns[:-1]

# Asignar las características normalizadas y las etiquetas al DataFrame final
df_cleaned_normalized = pd.concat([df_normalized, df_cleaned['label']], axis=1)

# Balancear el dataset
df_cleaned_balanced = balance_data(df_cleaned_normalized)

# Dividir los datos en entrenamiento y prueba de forma aleatoria
df_train, df_test = train_test_split(df_cleaned_balanced, test_size=0.25, random_state=42)

# Separar las características (X) y la etiqueta (y) para entrenamiento y prueba
X_train = df_train.drop(columns=['label']).values
y_train = df_train['label'].values
X_test = df_test.drop(columns=['label']).values
y_test = df_test['label'].values

# Escalar las características
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Calcular el vector promedio para cada clase y normalizarlo
def compute_class_centroids(X_train, y_train):
    class_labels = np.unique(y_train)
    centroids = {}
    for label in class_labels:
        class_vectors = X_train[y_train == label]
        centroid = np.mean(class_vectors, axis=0)
        # Normalizar el vector promedio
        centroids[label] = normalizar_vector(centroid)
    return centroids

# Calcular los centroides de clase
centroids = compute_class_centroids(X_train, y_train)

# Crear y entrenar el modelo de RandomForest
rf_model = RandomForestClassifier(max_depth=None, min_samples_split=2, n_estimators=50, random_state=42)
rf_model.fit(X_train, y_train)

# Crear y entrenar el modelo de LogisticRegression
lr_model = LogisticRegression(C=100, max_iter=500, penalty='l1', solver='liblinear', random_state=42)
lr_model.fit(X_train, y_train)

# Guardar los modelos y centroides
with open('rf_model.pkl', 'wb') as file:
    pickle.dump(rf_model, file)

with open('lr_model.pkl', 'wb') as file:
    pickle.dump(lr_model, file)

with open('centroids.pkl', 'wb') as file:
    pickle.dump(centroids, file)

with open('scaler.pkl', 'wb') as file:
    pickle.dump(scaler, file)

print("Modelos y centroides guardados exitosamente.")
