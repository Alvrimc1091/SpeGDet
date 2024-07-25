import logging
import socket
import asyncio
import subprocess
import os
import pandas as pd
from pathlib import Path
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configuración del token del bot de Telegram
TOKEN = "7327013745:AAH8hl6XfNlHoZcsoNtAlC9RU_wM6azxWiE"

# ID del chat donde enviarás la IP (puedes obtenerlo usando el bot de Telegram @userinfobot)
CHAT_ID = "5129990683"

# Directorios
PHOTO_DIR = "/home/pi/SpeGDet/DataMeassures/PhotoSensor"
CSV_FILE = "/home/pi/SpeGDet/DataMeassures/DataSensor/predicciones.csv"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

async def get_local_ip():
    """
    Obtiene la dirección IP local de la Raspberry Pi.
    """
    try:
        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))  # Conectar a un servidor externo (Google DNS)
        ip_address = sock.getsockname()[0]  # Obtener la dirección IP asignada a la interfaz de red
        sock.close()
        return ip_address
    except Exception as e:
        logger.error(f"Error al obtener la dirección IP: {e}")
        return None

async def send_ip_to_telegram():
    """
    Envía la dirección IP local al chat de Telegram especificado.
    """
    ip_address = await get_local_ip()
    if ip_address:
        bot = Bot(token=TOKEN)
        try:
            await bot.send_message(chat_id=CHAT_ID, text=f"La IP de esta Raspberry Pi es: {ip_address}")
            logger.info(f"IP enviada con éxito: {ip_address}")
        except Exception as e:
            logger.error(f"Error al enviar el mensaje de Telegram: {e}")
    else:
        logger.error("No se pudo recuperar la dirección IP.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /start.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="¡Hola! Soy tu bot de Raspberry Pi. Usa /ip para obtener la IP, /l para ejecutar el script led.py, /graindetector para ejecutar graindetector.py, /graindetector2 para ejecutar graindetector2.py y /getphoto para obtener la última foto.")

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /ip.
    """
    ip_address = await get_local_ip()
    if ip_address:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"La IP de esta Raspberry Pi es: {ip_address}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No se pudo recuperar la dirección IP.")

async def run_led_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /l que ejecuta el script led.py.
    """
    try:
        result = subprocess.run(["python3", "blinkled.py"], capture_output=True, text=True)
        if result.returncode == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Script ejecutado con éxito:\n{result.stdout}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al ejecutar el script:\n{result.stderr}")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al intentar ejecutar el script: {e}")

async def run_graindetector_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /graindetector que ejecuta graindetector.py con sudo.
    """
    try:
        result = subprocess.run(["sudo", "python3", "/home/pi/SpeGDet/ProdCode/graindetector.py"], capture_output=True, text=True)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ejecutando graindetector.py")
        if result.returncode == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Script ejecutado con éxito:\n{result.stdout}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al ejecutar el script con sudo:\n{result.stderr}")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al intentar ejecutar el script con sudo: {e}")

async def run_graindetector2_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /graindetector2 que ejecuta graindetector2.py con sudo.
    """
    try:
        # Ejecutar el script y redirigir la salida de error a un archivo
        result = subprocess.run(
            ["sudo", "python3", "/home/pi/SpeGDet/ProdCode/graindetector2.py"],
            capture_output=True,
            text=True
        )
        
        # Guardar los resultados en un archivo de log para revisión
        with open("/home/pi/SpeGDet/ProdCode/graindetector2.log", "w") as log_file:
            log_file.write(result.stdout)
            log_file.write(result.stderr)
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Ejecutando graindetector2.py")
        if result.returncode == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Script ejecutado con éxito:\n{result.stdout}")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al ejecutar el script con sudo:\n{result.stderr}")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al intentar ejecutar el script con sudo: {e}")

async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler para el comando /getphoto que envía la última foto y la información asociada al chat de Telegram.
    """
    try:
        # Obtener la última foto en términos de fecha y hora
        files = list(Path(PHOTO_DIR).glob('foto_*.jpg'))
        if files:
            latest_photo = max(files, key=os.path.getctime)
            
            # Leer el archivo CSV para encontrar la predicción asociada a la última foto
            df = pd.read_csv(CSV_FILE, header=None, names=["fecha", "valores", "foto", "dist_euc", "rf", "log_reg"], sep=',')
            logger.info(f"DataFrame cargado:\n{df.head()}")  # Verifica los primeros registros del DataFrame
            
            latest_photo_name = latest_photo.name
            logger.info(f"Última foto detectada: {latest_photo_name}")
            
            # Verificar nombres de fotos en el DataFrame
            fotos_en_df = df['foto'].unique()
            logger.info(f"Nombres de fotos en el DataFrame: {fotos_en_df}")
            
            # Buscar la fila correspondiente a la última foto
            pred_info = df[df["foto"].str.strip() == latest_photo_name]
            
            if not pred_info.empty:
                pred_info = pred_info.iloc[0]
                
                # Crear el mensaje de texto con la información de la predicción
                mensaje = (
                    f"Fecha: {pred_info['fecha']},\n"
                    f"Foto: {latest_photo_name}\n"
                    f"Predicción por Distancia Euclidiana: {pred_info['dist_euc']}\n"
                    f"Predicción por Random Forest: {pred_info['rf']}\n"
                    f"Predicción por Logistic Regression: {pred_info['log_reg']}"
                )
                
                # Enviar la foto y la información al chat de Telegram
                with open(latest_photo, 'rb') as photo_file:
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=mensaje)
                
                logger.info(f"Última foto y predicción enviada: {latest_photo_name}")
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontró información de predicción para la foto.")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="No se encontraron fotos en el directorio.")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error al intentar enviar la foto y la predicción: {e}")

async def main():
    """
    Función principal que configura los comandos del bot y envía la IP al iniciar el script.
    """
    # Enviar la IP al iniciar el script
    await send_ip_to_telegram()

if __name__ == "__main__":
    # Configurar el bot
    application = ApplicationBuilder().token(TOKEN).build()

    # Añadir handlers para los comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ip", ip))
    application.add_handler(CommandHandler("l", run_led_script))
    application.add_handler(CommandHandler("graindetector", run_graindetector_script))
    application.add_handler(CommandHandler("graindetector2", run_graindetector2_script))
    application.add_handler(CommandHandler("getphoto", get_photo))

    # Ejecutar el bucle de eventos del bot
    application.run_polling()
