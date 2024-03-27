import I2C_LCD_driver
from time import *
import subprocess

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string("Hola mundo.", 1)

# Hola mundo en diferentes columnas

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string("Hola mundo.", 2, 3)

# Limpiar pantalla

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string("Texto en pantalla", 1)
sleep(1)

mylcd.lcd_clear()

mylcd.lcd_display_string("Limpia pantalla", 1)
sleep(1)

mylcd.lcd_clear()

# Parpadeo
mylcd = I2C_LCD_driver.lcd()

while True:
    mylcd.lcd_display_string(u"Hola mundo.")
    time.sleep(1)
    mylcd.lcd_clear()
    time.sleep(1)

# Mostrar la hora
mylcd = I2C_LCD_driver.lcd()


while True:
    mylcd.lcd_display_string("Hora: %s" %time.strftime("%H:%M:%S"), 1)
    
    mylcd.lcd_display_string("Fecha: %s" %time.strftime("%m/%d/%Y"), 2)

# Dirección IP

mylcd = I2C_LCD_driver.lcd()

IP = subprocess.check_output(["hostname", "-I"]).split()[0]

mylcd.lcd_display_string("IP:", 1) 
mylcd.lcd_display_string(str(IP),2)
