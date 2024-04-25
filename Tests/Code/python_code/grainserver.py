# RPI Zero 2W funcionará como servidor, PC como cliente

# --------
# Servidor
# --------

# Debe enviar datos del sensor y proyectar resultado en pantalla
# Datos y foto deben ser guardados en SD
# Se puede crear rutina para subir los datos al Github

# TO DO
# Establecer conexión servidor (RPI) - cliente (PC) (REVISAR)
# Guardar datos en .csv de la misma forma que se hace actualmente (REVISAR)
# Script para tomar datos y fotos una única vez (OK)
# Realizar calibración y estimación de granos 

import socket
import time
import threading
import os
import board
import time
import datetime
import zoneinfo
import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización del sensor AS7341
sensor = AS7341(board.I2C())

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# Lista básica de comandos
COMMANDS = {
    "1": "ls",
    "2": "pwd",
    "3": "echo Hello, world!",
    "exit": "exit",
    "q": "exit"
}

def manejar_comandos(client_socket):
    try:
        while True:
            command = input("Ingrese un comando (escriba 'list' para mostrar comandos disponibles): ")
            if command.lower() == "list":
                print("Comandos disponibles")
                for key, value in COMMANDS.items():
                    print(f"{key}: {value}")
                continue
            
            elif command in COMMANDS:
                # command_to_send = COMMANDS[command]
                # client_socket.send(command_to_send.encode())

                if command == "exit" or command == "q":
                    hora_santiago = datetime.datetime.now(zona_santiago)
                    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Cerrando Servidor")
                    client_socket.close()
                    os._exit(0)
            else:
                print("Comando inválido. Ingrese 'list' para mostrar comando disponibles ")

    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        client_socket.close()


# Definición de guardar_foto
# 
def guardar_foto(HOST, PORT):

    try:
        # Inicializar cámara
        picam2.start()
        time.sleep(1)

        # Ciclo para guardar la foto
        while True:
            # Crea la foto con el nombre de la hora indicada
            hora_santiago = datetime.datetime.now()  # Obtiene la hora actual
            fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
            foto_id = f"foto_up_{fecha_hora_actual}.jpg"

            # Toma la foto y llama a la función para enviar la foto
            picam2.capture_file(foto_id)
            time.sleep(1)
            enviar_foto(HOST, PORT, foto_id)

            # Guarda la foto con el nombre de la hora indicada
            with open(foto_id, "ab") as f:  # Modo "ab" para escritura binaria y anexar
                f.write(data)
                print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada como {foto_id}")
            
            # Guarda información de la foto en el archivo CSV
            datos_a_csv("", foto_id)
            os.remove(foto_id)

            # Vuelve a repetir el ciclo cada 60 seg
            time.sleep(60)
    
    # Rutina para manejar errores
    except Exception as e:
        print("Error al guardar la foto:", e)

# Definición de enviar_foto
# 
def enviar_foto(HOST, PORT, foto_id):
    try:
        # Establece la conexión con los clientes para enviar la foto
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            # Entra al ciclo para enviar la foto
            while True:
                # hora_santiago = datetime.datetime.now(zona_santiago)
                # nombre_foto = f"foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

                # Envía la foto al servidor e imprime el mensaje
                with open(foto_id, "rb") as f:
                    data = f.read()
                    s.sendall(data)
                    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {foto_id} enviada al servidor")
    
    # Rutina para manejar errores
    except Exception as e:
        print("Error al enviar la foto:", e)

# Definición guardar_datos_sensor
# 
def guardar_datos_sensor(client_socket):
    try:
        # Ciclo para obtener y guardar los datos del sensor
        while True:
            data = ",".join(map(str, datos_sensor()))  # Obtener datos del sensor y convertirlos a cadena
            hora_santiago = datetime.datetime.now(zona_santiago)

            # Guarda la foto y datos en un CSV
            foto_id = f"foto_up_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
            datos_a_csv(data, foto_id)

            # Envía los datos a los clientes
            enviar_datos_sensor(client_socket, data)
            
            # Muestra la información en pantalla
            lcd.lcd_clear()
            lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
            lcd.lcd_display_string("Datos guardados", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")

            # Vuelve a repetir el ciclo cada 60 segundos
            time.sleep(60)

    except Exception as e:
        print("Error al guardar los datos:", e)

# Definición enviar_datos_sensor
# Envía los datos recopilados por
def enviar_datos_sensor(client_socket, data):
    try:
        while True:
            client_socket.send(data.encode())

    except Exception as e:
        print("Error sending data:", e)

# Definición datos_a_csv
# 
def datos_a_csv(datos, foto_id):
    datos = datos.split(",")

    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
    datos.append(foto_id)

    with open("data_test.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)


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

# ------
# Procesamiento para estimar el grano
# ------

# ------
# Función principal
# ------

def main():

    # Definición de los parámetros del servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.3.101' # Ingresar IP de RPI
    port = 8080 # Ingresar puerto para sensor superior/inferior (deben ser diferente)
    server.bind((host, port))  # Enlaza el servidor a la dirección IP y puerto especificados
    server.listen(5)
    hora_santiago = datetime.datetime.now(zona_santiago)
    
    # Inicialización del servidor
    # Se muestran mensajes en consola y en pantalla
    lcd.lcd_clear()
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string("Enviando datos", 2)    
    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Escuchando en {host}:{port} and Listening on {host}:{port+1}")
    time.sleep(3)


    while True:
        # Inicialización sockets y establecimiento de conexiones
        client_socket, addr = server.accept()
        hora_santiago = datetime.datetime.now(zona_santiago)
        print("[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Conexión entrante en: %s:%d" % (addr[0], addr[1]))

        # Inicia el hilo para obtener datos periódicamente 
        datos_thread = threading.Thread(target=guardar_datos_sensor, args=(client_socket,))
        datos_thread.start()

        # Inicia el hilo para obtener la foto periódicamente 
        fotos_thread = threading.Thread(target=guardar_foto, args=(host, port+1))
        fotos_thread.start()

        # Inicia el hilo para manejar comandos
        command_handler = threading.Thread(target=manejar_comandos, args=(client_socket,))
        command_handler.start()

if __name__ == "__main__":
    main()