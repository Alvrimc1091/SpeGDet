import os
import sys
import time
from led_functions import encender_led, secuencia_led_inicializacion, blink_leds, led_blue, led_red, led_yellow, led_green

# Asegúrate de que el directorio actual esté en el path para permitir las importaciones
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importar la función main de rpisensor
from rpisensor import main as rpisensor_main

# Importar la función predict_grain_from_csv de grainclass
from grainclass import predict_grain_from_csv

# Definir la ruta del archivo CSV
csv_file_path = "/home/pi/SpeGDet/DataMeassures/DataSensor/data_sensor.csv"


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
    
    predictions = predict_grain_from_csv(csv_file_path)
    
    # Manejar la predicción encendiendo el LED adecuado
    manejar_prediccion(predictions)

if __name__ == "__main__":
    main()
