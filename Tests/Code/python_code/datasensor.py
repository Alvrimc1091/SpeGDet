# Script para tomar datos de la muestra
import csv
import socket
import math
import time
import threading
import os
import board
import time
import datetime
import zoneinfo
from gpiozero import LED
import I2C_LCD_driver
from adafruit_as7341 import AS7341
from picamera2 import Picamera2, Preview

# Definición del arreglo de LEDs
led_array = LED(17)

# Definición de pantalla LCD como variable "lcd"
lcd = I2C_LCD_driver.lcd()

# Zona horaria
zona_santiago = zoneinfo.ZoneInfo("America/Santiago")

# Inicialización del sensor AS7341
sensor = AS7341(board.I2C())

# sensor.setatime = 1
# sensor.setASTEP = 10

# Valores de Ganancia 
#   Parámetro      ||   Valor
# sensor.gain = 0  ||     0.5
# sensor.gain = 1  ||      1
# sensor.gain = 2  ||      2
# sensor.gain = 3  ||      4
# sensor.gain = 4  ||      8
# sensor.gain = 5  ||      16
# sensor.gain = 6  ||      32
# sensor.gain = 7  ||      64
# sensor.gain = 8  ||      128
# sensor.gain = 9  ||      256
# sensor.gain = 10 ||      512

# print(sensor.atime)
# print(sensor.astep)
# print(sensor.gain) #= 512

# Sensor ATIME (Por defecto es 100)
# sensor.atime = 29

# Sensor ASTEP (Por defecto es 999)
# sensor.astep = 599

# Con ATIME = 29 y ASTEP = 599 se tiene t_int igual a 50ms
# Con ATIME = 100 y ASTEP = 999 se tiene t_int igual a 280ms


#sensor.gain = 10
# Definición de contador total de muestras
meassurement = 1

# Definición del threshold
threshold = 100

# sensor.led = 

# Configuración inicial de la cámara
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration() 
picam2.configure(camera_config) 
picam2.start_preview(Preview.NULL)

# -------------------------------------------------------------------
# ----------------- Base de datos de las muestras -------------------
# -------------------------------------------------------------------

# --------------------- Muestras Puras (100%) -----------------------

# ----------------------- Muestras (100%) ---------------------------

# Base de datos para la luz blanca
luzblanca_db = [770.8, 6034.7, 2179.6, 3800.3, 4651.4, 3841.8, 2659.8, 1182.7]
#, 13999.6, 469.3]

# Base de datos para el trigo
trigo_db = [178.71428571428572, 1705.0, 831.3333333333334, 1354.5714285714287, 2192.3333333333335, 2167.4761904761904, 1631.7619047619048, 1038.4761904761904]
#[159.2, 1328.8, 662.0, 1208.1, 2060.0, 2075.8, 1581.8, 1065.6] # Promedio muestras movimiento y cristal

# Promedio datos estáticos = [159.2, 1328.8, 662.0, 1208.1, 2060.0, 2075.8, 1581.8, 1065.6]
# Promedio Total = [275.68, 2830.8, 1196.76, 2126.4, 3114.0, 2992.44, 2073.2, 1286.24]

#[154.0, 1338.0, 655.0, 1225.0, 2049.0, 2068.0, 1549.0, 1018.0]
#[156.0, 1314.0, 649.0, 1191.0, 2009.0, 2035.0, 1559.0, 1049.0]
#[161.0, 1369.0, 679.0, 1249.0, 2120.0, 2144.0, 1637.0, 1091.0]
#[154.0, 1294.0, 638.0, 1177.0, 1993.0, 2000.0, 1516.0, 1016.0]
#[157.0, 1280.0, 643.0, 1194.0, 2065.0, 2074.0, 1586.0, 1069.0]
#[155.0, 1294.0, 650.0, 1176.0, 2039.0, 2056.0, 1559.0, 1068.0]
#[167.0, 1373.0, 681.0, 1223.0, 2094.0, 2101.0, 1598.0, 1079.0]
#[164.0, 1340.0, 677.0, 1228.0, 2079.0, 2105.0, 1611.0, 1080.0]
#[167.0, 1395.0, 697.0, 1245.0, 2117.0, 2129.0, 1635.0, 1113.0]
#[157.0, 1291.0, 651.0, 1173.0, 2035.0, 2046.0, 1568.0, 1073.0]

# Movimiento
#[172.0, 1253.0, 648.0, 1050.0, 1715.0, 1673.0, 1365.0, 919.0]
#[191.0, 1402.0, 684.0, 1147.0, 1934.0, 1877.0, 1488.0, 1015.0]
#[230.0, 1585.0, 778.0, 1228.0, 2174.0, 1992.0, 1556.0, 953.0]
#[155.0, 1240.0, 650.0, 1116.0, 1861.0, 1840.0, 1441.0, 962.0]
#[152.0, 1190.0, 640.0, 1052.0, 1973.0, 1869.0, 1491.0, 936.0]

# Cristal
#[446.0, 5427.0, 2128.0, 3736.0, 5074.0, 4721.0, 3038.0, 1754.0]
#[443.0, 5481.0, 2142.0, 3755.0, 5097.0, 4750.0, 3047.0, 1766.0]
#[440.0, 5651.0, 2196.0, 3822.0, 5179.0, 4819.0, 3081.0, 1794.0]
#[438.0, 5475.0, 2140.0, 3732.0, 5083.0, 4705.0, 3022.0, 1754.0]
#[427.0, 5526.0, 2142.0, 3720.0, 5072.0, 4726.0, 3030.0, 1787.0]
#[434.0, 5485.0, 2126.0, 3728.0, 5052.0, 4759.0, 3026.0, 1779.0]
#[421.0, 4815.0, 1860.0, 3393.0, 4430.0, 4282.0, 2700.0, 1605.0]
#[430.0, 4783.0, 1858.0, 3407.0, 4443.0, 4310.0, 2726.0, 1609.0]
#[457.0, 4187.0, 1685.0, 3147.0, 4109.0, 3929.0, 2507.0, 1463.0]
#[464.0, 3982.0, 1622.0, 3046.0, 4054.0, 3801.0, 2494.0, 1404.0]

# Old Data
# -------------------------------------------------------------------
#[154.6, 1346.9, 664.7, 1306.3, 2091.5, 2101.7, 1581.5, 973.2]#, 4204.8, 241.1]
#[152.0, 1306.7, 653.1, 1274.8, 2014.1, 2096.3, 1597.7, 978.0, 5074.0, 281.6]
# -------------------------------------------------------------------

# Base de datos para el maíz
maiz_db = [245.0, 2041.85, 1036.85, 1781.6, 3382.75, 3404.25, 2522.4, 1536.85]
#[237.0, 1701.1, 904.8, 1692.9, 3570.5, 3564.4, 2690.7, 1725.4] # Promedio muestras movimiento y cristal

# Promedio estático =  [237.0, 1701.1, 904.8, 1692.9, 3570.5, 3564.4, 2690.7, 1725.4]
# Promedio Maiz Total = [366.916666, 2734.458333, 1263.291666, 2405.625, 4256.416666, 4093.833333, 2992.75, 1759.791666]
#[242.0, 1751.0, 911.0, 1702.0, 3520.0, 3611.0, 2728.0, 1713.0]
#[245.0, 1923.0, 1045.0, 1882.0, 3866.0, 3744.0, 2853.0, 1815.0]
#[241.0, 1513.0, 885.0, 1584.0, 3544.0, 3408.0, 2676.0, 1722.0]
#[253.0, 1728.0, 898.0, 1770.0, 3658.0, 3665.0, 2754.0, 1740.0]
#[237.0, 1735.0, 870.0, 1661.0, 3487.0, 3509.0, 2587.0, 1700.0]
#[239.0, 1636.0, 890.0, 1749.0, 3714.0, 3740.0, 2781.0, 1764.0]
#[222.0, 1645.0, 863.0, 1669.0, 3574.0, 3568.0, 2688.0, 1698.0]
#[246.0, 1779.0, 936.0, 1706.0, 3657.0, 3704.0, 2739.0, 1807.0]
#[225.0, 1732.0, 907.0, 1664.0, 3281.0, 3303.0, 2466.0, 1618.0]
#[220.0, 1569.0, 843.0, 1542.0, 3404.0, 3392.0, 2635.0, 1677.0]

# Movimiento
#[238.0, 1753.0, 931.0, 1733.0, 3427.0, 3375.0, 2512.0, 1609.0]
#[197.0, 1293.0, 731.0, 1317.0, 3122.0, 3052.0, 2391.0, 1493.0]
#[203.0, 1456.0, 790.0, 1405.0, 3160.0, 3089.0, 2375.0, 1506.0]
#[211.0, 1369.0, 779.0, 1399.0, 3086.0, 3049.0, 2387.0, 1521.0]
#[246.0, 1821.0, 940.0, 1767.0, 3415.0, 3375.0, 2536.0, 1626.0]

# Cristal
#[584.0, 4424.0, 1851.0, 3594.0, 5351.0, 4952.0, 3517.0, 1818.0]
#[602.0, 5024.0, 2103.0, 4037.0, 6156.0, 5787.0, 4038.0, 2096.0]
#[608.0, 4929.0, 2077.0, 3996.0, 6074.0, 5641.0, 3933.0, 2048.0]
#[613.0, 4658.0, 1964.0, 3803.0, 5851.0, 5410.0, 3767.0, 1999.0]
#[588.0, 4414.0, 1835.0, 3580.0, 5392.0, 5005.0, 3502.0, 1861.0]
#[602.0, 4515.0, 1886.0, 3626.0, 5583.0, 5171.0, 3653.0, 1953.0]
#[583.0, 4246.0, 1758.0, 3466.0, 5266.0, 4895.0, 3415.0, 1835.0]
#[587.0, 4384.0, 1825.0, 3583.0, 5376.0, 5011.0, 3517.0, 1841.0]
#[574.0, 4330.0, 1801.0, 3500.0, 5190.0, 4796.0, 3376.0, 1775.0]

# Old Data
#[227.0, 1552.3, 790.3, 1812.3, 3524.2, 3653.9, 2695.7, 1479.4]#, 6352.3, 391.4]
#[260.0, 2083.1, 1073.0, 2189.6, 4200.4, 4244.7, 3097.0, 1841.8, 9451.1, 533.2]



# Base de datos para la poroto

poroto_db = [177.8, 1629.6, 830.8, 1427.1, 2325.3, 2318.65, 1727.7, 1135.9]
#[151.1, 1129.2, 652.1, 1184.4, 2179.4, 2155.4, 1684.3, 1206.7] # Promedio en movimiento y cristal 

# Promedio muestras estáticas = [151.1, 1129.2, 652.1, 1184.4, 2179.4, 2155.4, 1684.3, 1206.7]
# Promedio total = [303.538461, 2252.0, 1054.923076, 1984.230769, 3058.846153, 2878.961538, 2148.923076, 1331.538461]
#[139.0, 1082.0, 612.0, 1142.0, 2104.0, 2098.0, 1582.0, 1174.0]
#[136.0, 1008.0, 589.0, 1019.0, 1955.0, 1934.0, 1543.0, 1145.0]
#[155.0, 1089.0, 643.0, 1162.0, 2121.0, 2147.0, 1708.0, 1212.0]
#[151.0, 1127.0, 655.0, 1221.0, 2250.0, 2208.0, 1726.0, 1234.0]
#[163.0, 1240.0, 713.0, 1276.0, 2338.0, 2294.0, 1801.0, 1259.0]
#[152.0, 1071.0, 638.0, 1160.0, 2164.0, 2150.0, 1691.0, 1200.0]
#[154.0, 1165.0, 658.0, 1218.0, 2205.0, 2180.0, 1687.0, 1178.0]
#[162.0, 1214.0, 700.0, 1256.0, 2305.0, 2231.0, 1719.0, 1215.0]
#[153.0, 1165.0, 674.0, 1214.0, 2225.0, 2191.0, 1722.0, 1237.0]
#[146.0, 1131.0, 639.0, 1176.0, 2127.0, 2121.0, 1664.0, 1213.0]
#[144.0, 1103.0, 626.0, 1162.0, 2103.0, 2075.0, 1625.0, 1170.0]

# Movimiento
#[143.0, 977.0, 617.0, 1006.0, 1798.0, 1671.0, 1407.0, 968.0]
#[153.0, 939.0, 619.0, 961.0, 2117.0, 2061.0, 1684.0, 1175.0]
#[158.0, 1129.0, 675.0, 1142.0, 2119.0, 2098.0, 1671.0, 1172.0]
#[160.0, 1081.0, 662.0, 1092.0, 2002.0, 1973.0, 1605.0, 1110.0]
#[147.0, 1044.0, 594.0, 1071.0, 1867.0, 1937.0, 1557.0, 1099.0]

# Cristal
#[532.0, 4054.0, 1701.0, 3312.0, 4568.0, 4170.0, 2923.0, 1570.0]
#[533.0, 4058.0, 1698.0, 3295.0, 4527.0, 4123.0, 2918.0, 1576.0]
#[536.0, 4069.0, 1706.0, 3301.0, 4566.0, 4147.0, 2928.0, 1602.0]
#[557.0, 4186.0, 1752.0, 3399.0, 4674.0, 4239.0, 3011.0, 1623.0]
#[557.0, 4170.0, 1745.0, 3388.0, 4641.0, 4202.0, 2995.0, 1602.0]
#[554.0, 4122.0, 1718.0, 3347.0, 4576.0, 4137.0, 2940.0, 1577.0]
#[551.0, 4132.0, 1726.0, 3352.0, 4585.0, 4163.0, 2953.0, 1584.0]
#[550.0, 4138.0, 1725.0, 3353.0, 4590.0, 4185.0, 2978.0, 1598.0]
#[538.0, 3798.0, 1555.0, 3087.0, 4220.0, 3804.0, 2728.0, 1476.0]
#[568.0, 4260.0, 1788.0, 3478.0, 4783.0, 4314.0, 3106.0, 1651.0]

# Old Data
#[146.0, 1044.0, 598.2, 1256.3, 2112.8, 2191.6, 1701.0, 1132.1]#, 4349.1, 270.7]
#[169.3, 1412.0, 754.8, 1525.2, 2449.0, 2579.1, 1958.6, 1315.9, 6339.1, 373.7]

# ------------------- Muestras mezcladas (50/50) --------------------

# Base de datos para trigo/maiz
trigomaiz_db = [207.8, 1814.0, 919.4, 1558.1, 2796.0, 2781.85, 2096.25, 1317.2]

# Base de datos para trigo/poroto
trigoporoto_db = [176.8, 1646.5, 847.5, 1377.45, 2311.0, 2257.65, 1731.05, 1164.4]

# Base de datos para maiz/poroto
maizporoto_db = [208.5, 1799.8, 904.7, 1649.2, 2882.55, 2869.95, 2109.35, 1286.6]

# Diccionario con las muestras puras
muestraspuras_dic = {

        # "luz blanca": luzblanca_db,
        "trigo": trigo_db,
        "maiz": maiz_db,
        "poroto": poroto_db,
        "poroto/maiz": maizporoto_db,
        "trigo/maiz": trigomaiz_db,
        "trigo/poroto": trigoporoto_db
        
}

# -------------------------------------------------------------------
# ----------------------- Definición de funciones -------------------
# -------------------------------------------------------------------

# Definición bar_graph()
# Obtiene las lecturas de los 10+1 canales
def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

# Función para obtener los datos del sensor
def datos_sensor():
    # Obtiene las lecturas de los canales y los almacena en un diccionario
    datos_sensor = [
        bar_graph(sensor.channel_415nm),
        bar_graph(sensor.channel_445nm),
        bar_graph(sensor.channel_480nm),
        bar_graph(sensor.channel_515nm),
        bar_graph(sensor.channel_555nm),
        bar_graph(sensor.channel_590nm),
        bar_graph(sensor.channel_630nm),
        bar_graph(sensor.channel_680nm)
        # bar_graph(sensor.channel_clear),
        # bar_graph(sensor.channel_nir)
    ]
    return datos_sensor

def mostrar_datos():
    # print("------ Datos de la muestra ------")

    # print("F1 - 415nm/Violet  %s" % bar_graph(sensor.channel_415nm))
    # print("F2 - 445nm//Indigo %s" % bar_graph(sensor.channel_445nm))
    # print("F3 - 480nm//Blue   %s" % bar_graph(sensor.channel_480nm))
    # print("F4 - 515nm//Cyan   %s" % bar_graph(sensor.channel_515nm))
    # print("F5 - 555nm/Green   %s" % bar_graph(sensor.channel_555nm))
    # print("F6 - 590nm/Yellow  %s" % bar_graph(sensor.channel_590nm))
    # print("F7 - 630nm/Orange  %s" % bar_graph(sensor.channel_630nm))
    # print("F8 - 680nm/Red     %s" % bar_graph(sensor.channel_680nm))
    # print("Clear              %s" % bar_graph(sensor.channel_clear))
    # print("Near-IR (NIR)      %s" % bar_graph(sensor.channel_nir))

    # print("------------------------------------------")

    datos = datos_sensor()
    # promedio_datos_medida(datos)
    hora_santiago = datetime.datetime.now(zona_santiago)
    datos_str = ",".join(map(str, datos))
    foto_id = f"foto_up_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
    #guardar_datos(datos_str, foto_id, hora_santiago)
    return datos
    
def promedio_datos_medida(*filas):
    # Obtener el número de filas y el número de columnas
    num_filas = len(filas)
    num_columnas = len(filas[0])

    # Inicializar la matriz de datos
    datos_medida = [[0] * num_columnas for _ in range(num_filas)]

    # Llenar la matriz de datos con las filas proporcionadas
    for i in range(num_filas):
        for j in range(num_columnas):
            # Eliminar corchetes y asteriscos antes de convertir a entero
            valor = filas[i][j].replace("[", "").replace("]", "").replace("*", "").strip()
            datos_medida[i][j] = int(valor)
    
    # Calcular los promedios de cada columna
        promedios_columnas = [sum(columna) / len(columna) for columna in zip(*datos_medida)]
    
    return promedios_columnas

def distancia_euclidiana(vector_db, vector_medido):
    if len(vector_db) != len(vector_medido):
        raise ValueError("Los vectores deben tener la misma longitud")
    
    suma_cuadrados = sum((x - y) ** 2 for x, y in zip(vector_db, vector_medido))
    distancia = math.sqrt(suma_cuadrados)
    return distancia/100

def estimacion_grano(vector_db, vector_medida):
    hora_santiago = datetime.datetime.now(zona_santiago)
    distancias = {}
    
    for grano, vector_referencia in vector_db.items():
        distancia = distancia_euclidiana(vector_referencia, vector_medida)
        distancias[grano] = distancia
        print(f"Distancia euclidiana para {grano}: {distancia}")
    
    grano_identificado = min(distancias, key=distancias.get)
    distancia_minima = distancias[grano_identificado]
    
    if distancia_minima < threshold:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string(grano_identificado.capitalize(), 2)
        print(grano_identificado.capitalize())
        time.sleep(3)
    else:
        limpiar_pantalla(hora_santiago)
        lcd.lcd_display_string("Desconocido", 2)
        print("Grano desconocido")
        time.sleep(3)

def ejecutar_estimacion_grano(vector_medida):
    estimacion_grano(muestraspuras_dic, vector_medida)

def guardar_datos(datos, foto_id, hora_santiago):

    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Datos del sensor guardados")
    print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto guardada")
    foto_id = f"foto_up_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"

    datos = datos.split(",")
    # datos.append("")
    datos.append(foto_id)
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d,%H:%M:%S")

    with open(f"/home/pi/SpeGDet/Tests/Data/data_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.csv", mode='a', newline='') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv)
        escritor_csv.writerow([fecha_hora] + datos)

def tomar_foto():
    try:
        picam2.start()    
        hora_santiago = datetime.datetime.now(zona_santiago)
        nombre_foto = f"/home/pi/SpeGDet/Tests/Data/foto_{hora_santiago.strftime('%H%M%S_%d%m%Y')}.jpg"
        fecha_hora_actual = hora_santiago.strftime("%H%M%S_%d%m%Y")
        
        picam2.capture_file(nombre_foto)
        time.sleep(2)

        with open(nombre_foto, "rb") as f:
            data = f.read()
            #print(f"[{hora_santiago.strftime('%H:%M:%S de %d/%m/%Y')}] --- Foto {nombre_foto} guardada")        
        
        # Guardar información de la foto en el archivo CSV
        foto_id = f"foto_{fecha_hora_actual}.jpg"
        # guardar_datos("", foto_id, hora_santiago)

    except Exception as e:
        print("Error al tomar la foto")

def limpiar_pantalla(hora_santiago):
    lcd.lcd_clear()
    lcd.lcd_display_string(f"[{hora_santiago.strftime('%H:%M:%S')}]", 1)

def main():
    
    # Definición del vector de datos totales de la medida
    datos_medida_final = []

    hora_santiago = datetime.datetime.now(zona_santiago)

    # Comienza recopilando los datos de la muestra
    # Imprime un mensaje en pantalla
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Tomando datos", 2)
    time.sleep(1)

    # Rutina para tomar datos y foto
    # Toma los datos e inmediatamente la foto

    # Ejecutar mostrar_datos varias veces para agregar datos a la matriz
    for _ in range(meassurement):
        led_array.on()
        sensor.led_current = 30
        #sensor.led = True
        datos_medida_final.append(mostrar_datos())
    
    tomar_foto()
    sensor.led = False
    led_array.off()

    # Envía mensaje de que los datos fueron guardados
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Datos guardados", 2)
    time.sleep(1)

    # Envía mensaje de que la foto fue guardada
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Foto guardada", 2)
    time.sleep(1)

    # Cierre de la medición
    # Imprime mensaje de finalización de la medición
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Medicion lista", 2)
    time.sleep(1)

    # Procesamiento de la medición
    # Procesa los datos tomados y realiza la estimación
    limpiar_pantalla(hora_santiago)
    lcd.lcd_display_string("Procesando datos", 2)
    time.sleep(2)

    # promedior las columnas de los datos totales
    resultados = promedio_datos_medida(*datos_medida_final)
    print("Promedio de cada columna:", resultados)

    ejecutar_estimacion_grano(resultados)

if __name__ == "__main__":
    main()

