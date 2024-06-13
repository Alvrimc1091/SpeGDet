#!/bin/bash
sleep 3

# Directorio donde se generan los archivos
source_dir="/home/pi/Data/Photos"

# Directorio destino
target_dir="/home/pi/SpeGDet/Photos"

# Mover archivos al directorio destino
mv $source_dir/* $target_dir/

# Mensaje de confirmación
echo "Archivos movidos exitosamente."

# Mostrar mensaje en pantalla LCD
# Importante: Asegúrate de ajustar la siguiente línea según tu configuración de LCD

python3 - <<END
import I2C_LCD_driver
import time
import datetime
import zoneinfo

# Directorio donde se encuentran los logs
log_dir = "/home/pi/Raspi-Confgs/take_pictures.log"

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")
hora_santiago = datetime.datetime.now(zona_santiago)

# Rutina para mostrar mensaje

lcd.lcd_clear()
lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)
lcd.lcd_display_string("Fotos Movidas", 2)
time.sleep(3)
lcd.lcd_clear()

with open(log_dir, "a") as log_file:
	log_file.write(f"Fotos movidas correctamente a las {hora_santiago}\n")

END

# Operaciones de Git
cd /home/pi/SpeGDet || exit

git add .
git commit -m "Fotos agregadas"
git push origin main
