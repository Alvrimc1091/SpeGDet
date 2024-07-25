from gpiozero import LED
from time import sleep

led5 = LED(5) # Rojo
led6 = LED(6) # Verde
led17 = LED(17) # Blancos
led22 = LED(22) # Azul
led27 = LED(27) # Amarillo

for i in range(4):
    led5.on()
    led6.on()
    led17.on()
    led22.on()
    led27.on()
    print("leds encendidos")
    sleep(1)
    print("leds apagados")
    led5.off()
    led6.off()
    led17.off()
    led22.off()
    led27.off()
    sleep(1)
