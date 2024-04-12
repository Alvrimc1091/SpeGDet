import subprocess
import time
import datetime
import zoneinfo
import I2C_LCD_driver
import socket

# Inicializa el controlador LCD
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Variable para almacenar el estado anterior de la conexión
conexion_anterior = None

# Función para obtener la dirección IP
def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except:
        return "No disponible"

# Función para verificar la conexión al inicio
def check_initial_connection():
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"])
        return True
    except subprocess.CalledProcessError:
        return False

# Función para mostrar el mensaje en la pantalla LCD
def show_message(message):
    lcd.lcd_clear()
    hora_santiago = datetime.datetime.now(zona_santiago)
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string(message, 2)

# Función para mostrar mensaje de inicio con dirección IP
def show_startup_message():
    lcd.lcd_clear()
    hora_santiago = datetime.datetime.now(zona_santiago)
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string("RPI Encendida", 2)
    time.sleep(3)  # Muestra la inicialización durante 3 segundos
    ip_address = get_ip_address()
    show_message(f"IP:{ip_address}")
    time.sleep(5)  # Muestra la IP durante 5 segundos

# Función para mostrar mensaje de conexión establecida
def show_connection_established():
    show_message("Conexion establecida")
    time.sleep(5)  # Muestra el mensaje durante 5 segundos

# Función para mostrar mensaje de conexión perdida
def show_connection_lost():
    show_message("Conexion perdida")
    time.sleep(5)  # Muestra el mensaje durante 5 segundos

# Verifica la conexión al inicio
conexion_actual = check_initial_connection()
show_startup_message()

# Muestra el estado de la conexión
if conexion_actual:
    show_connection_established()
else:
    show_connection_lost()

# Limpia la pantalla antes de salir
lcd.lcd_clear()
