import subprocess
import time
import board
import datetime
import zoneinfo
import I2C_LCD_driver
import socket
from adafruit_as7341 import AS7341

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
    time.sleep(5)  # Muestra la inicialización durante 3 segundos
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

# Agregar un retraso de 30 segundos al inicio del programa
time.sleep(45)

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

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Función para verificar la conexión del sensor y la pantalla LCD
def conexion_sensor():
    try:
        # Intenta inicializar el sensor AS7341
        sensor = AS7341(board.I2C())
        # Si no hay errores al inicializar el sensor, retorna True
        return True
    except Exception as e:
        print("Error al inicializar el sensor:", e)
        return False

def conexion_lcd():
    try:
        lcd = I2C_LCD_driver.lcd()
        return lcd
    except Exception as e:
        print("Error al inicializar la pantalla LCD:", e)
        return None

def conexion_camara():
    try:
        # Intenta inicializar la cámara
        picam2 = Picamera2()
        camera_config = picam2.create_preview_configuration() 
        picam2.configure(camera_config) 
        picam2.start_preview(Preview.NULL)
        # Si no hay errores al inicializar la cámara, retorna True
        return True
    except Exception as e:
        print("Error al inicializar cámara: ", e)
        return False

print("Verificando conexiones con sensores. \n"
"Si la hora mostrada no es correcta, verificar conexión a internet.")
time.sleep(5)

if conexion_lcd():
    lcd = I2C_LCD_driver.lcd()
    lcd.lcd_clear()
    hora_santiago = datetime.datetime.now(zona_santiago)
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
    lcd.lcd_display_string("Inicializando", 2)
    print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Pantalla LCD encontrada.")
    time.sleep(5)

    if conexion_sensor:
        lcd.lcd_clear()
        hora_santiago = datetime.datetime.now(zona_santiago)
        lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
        lcd.lcd_display_string("Sensor OK", 2)
        print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Sensor encontrado.")
        time.sleep(5)

        if conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
            lcd.lcd_display_string("Camara OK", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara encontrada.")
            time.sleep(5)
            lcd.lcd_clear()
        
        elif not conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
            lcd.lcd_display_string("Error Camara", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara no encontrada. Revise su conexión...")
            time.sleep(5)
            lcd.lcd_clear()
    
    elif not conexion_sensor:
        lcd.lcd_clear()
        hora_santiago = datetime.datetime.now(zona_santiago)
        lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
        lcd.lcd_display_string("Error Sensor", 2)
        print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Sensor no encontrado.")
        time.sleep(5)
        
        if conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
            lcd.lcd_display_string("Camara OK", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara encontrada.")
            time.sleep(5)
            lcd.lcd_clear()
        
        elif not conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
            lcd.lcd_display_string("Error Camara", 2)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara no encontrada. Revise su conexión...")
            time.sleep(5)
            lcd.lcd_clear()

elif not conexion_lcd():
    hora_santiago = datetime.datetime.now(zona_santiago)
    print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Pantalla LCD no encontrada...")

    if conexion_sensor:
        lcd.lcd_clear()
        hora_santiago = datetime.datetime.now(zona_santiago)
        print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Sensor encontrado.")
        time.sleep(5)

        if conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara encontrada.")
            time.sleep(5)
            lcd.lcd_clear()
            
        
        elif not conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara no encontrada.")
            time.sleep(5)
            lcd.lcd_clear()
        
    elif not conexion_sensor:
        lcd.lcd_clear()
        hora_santiago = datetime.datetime.now(zona_santiago)
        print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Sensor no encontrado.")
        time.sleep(5)

        if conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara encontrada.")
            time.sleep(5)
            lcd.lcd_clear()
            
        
        elif not conexion_camara:
            lcd.lcd_clear()
            hora_santiago = datetime.datetime.now(zona_santiago)
            print(f"[{hora_santiago.strftime('%H:%M:%S')}] ----- Cámara no encontrada.")
            time.sleep(5)
            lcd.lcd_clear()