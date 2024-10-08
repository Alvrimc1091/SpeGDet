#!/bin/bash
sleep 15

# Directorio donde se generan los archivos
source_dir="/home/pi/Data/Photos"

# Directorio destino
target_dir="/home/pi/SpeGDet/Photos"

# Mover archivos al directorio destino
cp $source_dir/* $target_dir/

# Mensaje de confirmación
echo "Fotos copiadas de manera correcta a las $('+%H:%M:%S')"

# Mostrar mensaje en pantalla LCD

python3 - <<END

import sys
sys.path.append('/home/pi/Raspi-Confgs')

import I2C_LCD_driver
import time
import datetime
import zoneinfo

# Directorio donde se encuentran los logs
log_direc = "/home/pi/Raspi-Confgs/take_pictures.log"

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")
hora_santiago = datetime.datetime.now(zona_santiago)

# Rutina para mostrar mensaje
#time.sleep(10)
lcd.lcd_clear()
lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
lcd.lcd_display_string("Fotos Movidas", 2)
time.sleep(3)
lcd.lcd_clear()

with open(log_direc, "a") as log_file:
	log_file.write(f"Fotos movidas a las {hora_santiago}\n")

END

# Operaciones de Git
# cd /home/pi/SpeGDet || exit

# git add .
# git commit -m "Fotos agregadas"
# git push origin main
