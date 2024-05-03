import csv
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

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Definición recibir_foto
# 
def recibir_foto(HOST, PORT):
    try:
        # Establece la conexión con el servidor
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            # Entra en un ciclo para aceptar la conexión y recibir la foto
            while True:
                hora_santiago = datetime.datetime.now(zona_santiago)  # Obtiene la hora actual
                fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
                conn, addr = s.accept()      
                print(f'[{hora_santiago.strftime("%H%M%S_%d%m%Y")}] --- Conectado por', addr)

                # Establece la conexión en función de los datos que llegue
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        # Guarda la foto con la hora actual que fue recibida
                        hora_santiago = datetime.datetime.now(zona_santiago)  # Actualiza la hora actual
                        fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")  # Actualiza la fecha y hora actual
                        foto_id = f"/home/pi/SpeGDet/Tests/Data_Client/foto_{fecha_hora_actual}.jpg" # Cambiar en función del directorio presente en el cliente
                        foto_id_corta = f"foto_{fecha_hora_actual}.jpg"
                        with open(foto_id, "ab") as f:  # Modo "ab" para escritura binaria y anexar
                            f.write(data)
                            
                    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto recibida y guardada como {foto_id_corta}")
                    # Guardar información de la foto en el archivo CSV
                    foto_id = f"/home/pi/SpeGDet/Tests/Data_Client/foto_{fecha_hora_actual}.jpg"
                    # datos_a_csv("", foto_id)

    except Exception as e:
        print("Error al recibir la foto:", e)

# Definición recibir_datos
#
def recibir_datos(client_socket):
    try:
        while True:
            data = client_socket.recv(1024).decode()  # Recibe datos periódicos del servidor
            hora_santiago = datetime.datetime.now(zona_santiago)
            print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor recibidos \n {data}")
            foto_id = f"/home/pi/SpeGDet/Tests/Data_Client/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
            datos_a_csv(data, foto_id)

    except Exception as e:
        print("Error receiving data:", e)

# Definición datos_a_csv
# 
def datos_a_csv(datos, foto_id):
    datos = datos.split(",")  # Separar la cadena de datos en una lista de valores
    fecha_hora = datetime.datetime.now(zona_santiago).strftime("%Y-%m-%d,%H:%M:%S")
    datos.append(foto_id)  # Agregar el foto_id al final de los datos
 
    with open("/home/pi/SpeGDet/Tests/Data_Client/data_test.csv", mode='a', newline='') as archivo_csv: # Cambiar en función del directorio presente en el cliente
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)

def enviar_estado(host, port, estado):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(mensaje.encode())
            pritn("Mensaje enviado")
            time.sleep(30)

    # Rutina para manejar errores
    except Exception as e:
        print("Error al enviar el mensaje de estado:", e)

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.3.101'
    port = 8080
    server_address = (host, port)  # Enlaza el servidor a la dirección IP y puerto especificados
    client.connect(server_address)

    # Inicia el hilo para recibir datos periódicamente del servidor
    data_thread = threading.Thread(target=recibir_datos, args=(client,))
    data_thread.start()

    # Inicia el hilo para recibir foto periódicamente del servidor
    photo_thread = threading.Thread(target=recibir_foto, args=(host, port + 1))
    photo_thread.start()

    report_thread = threading.Thread(target=enviar_estado, args=(host, port + 3, estado))
    report_thread.start()
    
    try:
        while True:
            command = client.recv(1024).decode()  # Recibe comando desde el servidor
            if not command:
                break
            print("Command received:", command)
            if command == "exit":
                print("Closing connection...")
                os._exit(0)
            response = "Response to '{}'".format(command)  # Procesa el comando (placeholder)
            client.send(response.encode())  # Envía respuesta al servidor    

    except KeyboardInterrupt:
        print("Conexión Cerrada")

    finally:
        client.close()
if __name__ == "__main__":
    main()
