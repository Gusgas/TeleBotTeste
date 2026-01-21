import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.webhook.aiohttp import get_new_configured_app
from fastapi import FastAPI
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import os

API_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Configuração do bot e do dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

app = FastAPI()

# Função de webhook
@app.post("/webhook/{token}")
async def telegram_webhook(update: Update, token: str):
    if token != API_TOKEN:
        raise HTTPException(status_code=400, detail="Invalid token")
    await dp.process_update(update)
    return {"status": "ok"}

# Configuração do webhook com aiogram
async def on_start_webhook(dp):
    webhook_path = f"/webhook/{API_TOKEN}"
    await bot.set_webhook(f"https://YOUR_URL{webhook_path}")
    return webhook_path

# Inicializando o webhook
app.add_event_handler("startup", on_start_webhook(dp))

# Iniciar o servidor FastAPI
if __name__ == '__main__':
    from uvicorn import run
    run(app, host="0.0.0.0", port=8000)
