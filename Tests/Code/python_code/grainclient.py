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

def recibir_foto(HOST, PORT):


def recibir_datos(client_socket):

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '192.168.2.12'
    port = 8080
    server_address = (host, port)  # Enlaza el servidor a la dirección IP y puerto especificados
    client.connect(server_address)



if __name__ == "__main__":
    main()
