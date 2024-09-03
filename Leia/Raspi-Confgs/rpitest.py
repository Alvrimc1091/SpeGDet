import board
import time
import zoneinfo
import datetime
import I2C_LCD_driver
from adafruit_as7341 import AS7341

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


if conexion_lcd():
    print("Verificando conexiones con sensores. \n"
    "Si la hora mostrada no es correcta, verificar conexión a internet.")
    time.sleep(2)
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
    print("Verificando conexiones con sensores. \n"
    "Si la hora mostrada no es correcta, verificar conexión a internet.")
    time.sleep(2)
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



