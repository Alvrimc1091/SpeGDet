import subprocess
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Función de inicio
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('¡Hola! Soy tu bot. Envíame comandos para ejecutar scripts de Python.')

# Función para ejecutar blinkled.py
async def run_blinkled(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        result = subprocess.run(['python3', 'blinkled.py'], capture_output=True, text=True)
        output = result.stdout if result.stdout else 'Script blinkled.py ejecutado.'
        await update.message.reply_text(output)
    except Exception as e:
        await update.message.reply_text(f'Error al ejecutar blinkled.py: {e}')

# Función para ejecutar grainclass.py con sudo
async def run_grainclass(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        result = subprocess.run(['sudo', 'python3', 'grainclass.py'], capture_output=True, text=True)
        output = result.stdout if result.stdout else 'Script grainclass.py ejecutado.'
        await update.message.reply_text(output)
    except Exception as e:
        await update.message.reply_text(f'Error al ejecutar grainclass.py: {e}')

# Función principal
def main() -> None:
    # Reemplaza 'YOUR_TOKEN' con el token de tu bot
    application = Application.builder().token('7327013745:AAH8hl6XfNlHoZcsoNtAlC9RU_wM6azxWiE').build()

    # Manejar comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run_blinkled", run_blinkled))
    application.add_handler(CommandHandler("run_grainclass", run_grainclass))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
