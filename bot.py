import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from aiogram.webhook.aiohttp import get_new_configured_app
from aiogram import F
from fastapi import FastAPI
from aiogram.utils.executor import start_webhook
from aiogram.types import ParseMode
from aiogram.filters import CommandStart

# Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Assumindo que você está utilizando variáveis de ambiente
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # A URL do seu domínio (render.com ou outro)
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"  # Caminho do webhook
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"  # URL completa do webhook

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do Bot e Dispatcher
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# FastAPI app para gerenciar o Webhook
app = FastAPI()

# Definindo o comportamento do /start
@dp.message(CommandStart())
async def cmd_start(message):
    await message.answer("Olá! Eu sou um bot Telegram.")

# Função para lidar com as atualizações do webhook
@app.post("/webhook/{token}")
async def telegram_webhook(update: Update):
    if update.message:
        logger.info(f"Nova mensagem de {update.message.from_user.full_name}")
    await dp.feed_update(update)  # Processa a atualização de forma síncrona
    return "OK"

# Função para configurar o webhook
async def on_start():
    # Configurando o webhook no Telegram
    webhook = await bot.set_webhook(WEBHOOK_URL)
    if webhook:
        logger.info(f"Webhook configurado com sucesso para {WEBHOOK_URL}")

# Função para iniciar o webhook
if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_start=on_start,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
    )
