import I2C_LCD_driver
import time
mylcd = I2C_LCD_driver.lcd()


while True:
    mylcd.lcd_display_string("Hora: %s" %time.strftime("%H:%M:%S"), 1)
    
    mylcd.lcd_display_string("Fecha: %s" %time.strftime("%m/%d/%Y"), 2)