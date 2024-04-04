from picamera2 import Picamera2, Preview 
import time 
import datetime
import zoneinfo
import board
import I2C_LCD_driver
from adafruit_as7341 import AS7341

# ------------ Definición de AS7341 como variable "sensor"
i2c = board.I2C() 
sensor = AS7341(i2c)

# ------------ Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# ------------ Definición de cámara como variable "picam2"
picam2 = Picamera2() 
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)
picam2.start()

# ------------ Muestra el texto en la pantalla LCD

lcd.lcd_display_string('Foto tomada', 1)
time.sleep(1)
lcd.lcd_clear()

# ------------ Obtiene la hora actual y extrae HH:MM
# hora_actual = datetime.datetime.now()
# hora = hora_actual.hour
# mins = hora_actual.minute

zona_santiago = zoneinfo.ZoneInfo("America/Santiago")
hora_santiago = datetime.datetime.now(zona_santiago)
hora = hora_santiago.hour
mins = hora_santiago.minute

def guardar_datos():
    # ------------ Guarda la foto tomada como .jpg
    lcd.lcd_display_string("Guardada en:",1)
    lcd.lcd_display_string(f"{hora}:{mins}.jpg", 2)
    time.sleep(1)
    picam2.capture_file(f"{hora}:{mins}.jpg")

guardar_datos()

# ------------ Definición bar_graph()
# ------------ Obtiene las lecturas de los 10+1 canales
def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

# ------------ Muestra el resultado de las lecturas de los canales
print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
print("F2 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
print("F3 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
print("F4 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
print("Clear              %s" % bar_graph(sensor.channel_clear))
print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))
print("\n------------------------------------------------")
time.sleep(1)

#lcd.lcd_clear()

