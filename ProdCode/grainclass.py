import pandas as pd
import re
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import warnings
from sklearn.exceptions import ConvergenceWarning
import matplotlib

matplotlib.use('TkAgg')  # Configurar el backend TkAgg para la visualización

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
    'maiz_pure': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_puremaiz.csv",
    'maiz_shake': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_shakemaiz.csv",
    'maiz_cristal': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_cristalmaiz.csv",
    'trigo_pure': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_puretrigo.csv",
    'trigo_shake': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_shaketrigo.csv",
    'trigo_cristal': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_cristaltrigo.csv",
    'poroto_pure': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_pureporoto.csv",
    'poroto_cristal': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_cristalporoto.csv",
    'poroto_shake': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_shakeporoto.csv",
    'empty_clean': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_dirtyempty.csv",
    'empty_dirty': "/mnt/c/Users/aimc2/Documents/Granos/Data/data_cleanempty.csv"
}

# Leer y combinar todos los datos de grano
dfs = []
for key, path in file_paths.items():
    label = key.split('_')[0]  # Obtener 'maiz', 'trigo', 'poroto', 'empty' de las claves
    df = read_grain_data(path, label)
    dfs.append(df)

# Combinar todos los dataframes en uno solo
df_combined = pd.concat(dfs, ignore_index=True)

# Verificar la forma del DataFrame combinado
print("Forma del DataFrame combinado:", df_combined.shape)
print("Primeras filas del DataFrame combinado:\n", df_combined.head())

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
print("Primeras filas del DataFrame combinado:\n", normalized_features.head())

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

# Calcular la distancia euclidiana entre dos vectores
def euclidean_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)

# Clasificación basada en la distancia euclidiana
def classify_euclidean(X_test, centroids):
    y_pred = []
    for x in X_test:
        distances = {label: euclidean_distance(x, centroid) for label, centroid in centroids.items()}
        y_pred.append(min(distances, key=distances.get))
    return np.array(y_pred)

# Calcular los centroides de clase
centroids = compute_class_centroids(X_train, y_train)

# Realizar la clasificación basada en distancia euclidiana
y_pred_euclidean = classify_euclidean(X_test, centroids)
euclidean_accuracy = accuracy_score(y_test, y_pred_euclidean)
print(f'Euclidean Distance Accuracy: {euclidean_accuracy:.2f}')

# Hiperparámetros óptimos para RandomForest y LogisticRegression
rf_params = {'max_depth': None, 'min_samples_split': 2, 'n_estimators': 50}
lr_params = {'C': 100, 'max_iter': 500, 'penalty': 'l1', 'solver': 'liblinear'}

# Crear y entrenar el modelo de RandomForest con validación cruzada
rf_model = RandomForestClassifier(**rf_params, random_state=42)
rf_model.fit(X_train, y_train)

# Validación cruzada para RandomForest
rf_cv_scores = cross_val_score(rf_model, X_train, y_train, cv=10)
print(f'Random Forest Cross-Validation Accuracy: {rf_cv_scores.mean():.2f} ± {rf_cv_scores.std():.2f}')

# Crear y entrenar el modelo de LogisticRegression con validación cruzada
lr_model = LogisticRegression(**lr_params, random_state=42)
lr_model.fit(X_train, y_train)

# Matriz de confusión y reporte de clasificación para Euclidean Distance
ed_cm = confusion_matrix(y_test, y_pred_euclidean)
ed_cr = classification_report(y_test, y_pred_euclidean)
print("Euclidean Distance Confusion Matrix:\n", ed_cm)
print("Euclidean Distance Classification Report:\n", ed_cr)

# Mostrar la matriz de confusión para la distancia euclidiana
ConfusionMatrixDisplay(confusion_matrix=ed_cm, display_labels=np.unique(y_train)).plot()
plt.title("Euclidean Distance Confusion Matrix")
plt.show()

# Validación cruzada para LogisticRegression
lr_cv_scores = cross_val_score(lr_model, X_train, y_train, cv=10)
print(f'Logistic Regression Cross-Validation Accuracy: {lr_cv_scores.mean():.2f} ± {lr_cv_scores.std():.2f}')

# Realizar predicciones y evaluar el modelo de RandomForest
y_pred_rf = rf_model.predict(X_test)
rf_accuracy = accuracy_score(y_test, y_pred_rf)
print(f'Random Forest Accuracy: {rf_accuracy:.2f}')

# Matriz de confusión y reporte de clasificación para RandomForest
rf_cm = confusion_matrix(y_test, y_pred_rf)
rf_cr = classification_report(y_test, y_pred_rf)
print("Random Forest Confusion Matrix:\n", rf_cm)
print("Random Forest Classification Report:\n", rf_cr)

# Mostrar la matriz de confusión para RandomForest
ConfusionMatrixDisplay(confusion_matrix=rf_cm, display_labels=rf_model.classes_).plot()
plt.title("Random Forest Confusion Matrix")
plt.show()

# Realizar predicciones y evaluar el modelo de LogisticRegression
y_pred_lr = lr_model.predict(X_test)
lr_accuracy = accuracy_score(y_test, y_pred_lr)
print(f'Logistic Regression Accuracy: {lr_accuracy:.2f}')

# Matriz de confusión y reporte de clasificación para LogisticRegression
lr_cm = confusion_matrix(y_test, y_pred_lr)
lr_cr = classification_report(y_test, y_pred_lr)
print("Logistic Regression Confusion Matrix:\n", lr_cm)
print("Logistic Regression Classification Report:\n", lr_cr)

# Mostrar la matriz de confusión para LogisticRegression
ConfusionMatrixDisplay(confusion_matrix=lr_cm, display_labels=lr_model.classes_).plot()
plt.title("Logistic Regression Confusion Matrix")
plt.show()
