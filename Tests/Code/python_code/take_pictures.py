import math
import time
import board
import time
import datetime
import zoneinfo
from gpiozero import LED
import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview


led_array = LED(17)
lcd = I2C_LCD_driver.lcd()

zona_santiago = zoneinfo.ZoneInfo("America/Santiago")


picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
picam2.start_preview(Preview.NULL)

def tomar_foto():
	try:
		led_array.on()
		picam2.start()
		
		hora_santiago = datetime.datetime.now(zona_santiago)
		nombre_foto = f"/home/pi/Data/Photos/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

		fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
		picam2.capture_file(nombre_foto)
		time.sleep(2)
		led_array.off()

	except Exception as e:
		print("Error al tomar la foto")
		
def limpiar_pantalla(hora_santiago):
	lcd.lcd_clear()
	lcd.lcd_display_string(f"Hora", 1)

def main():
	limpiar_pantalla(zona_santiago)
	lcd.lcd_display_string("Tomando fotos", 2)
	time.sleep(1)

	tomar_foto()
	
	limpiar_pantalla(zona_santiago)
	lcd.lcd_display_string("Foto guardada", 2)
	time.sleep(2)

if __name__ == "__main__":
	main()
		
