import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

# --------------------
# Configurações
# --------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL pública configurada no Telegram

if not TELEGRAM_TOKEN or not WEBHOOK_URL:
    raise RuntimeError("Telegram token ou webhook URL não configurados nas variáveis de ambiente!")

# --------------------
# Inicialização
# --------------------
bot = Bot(token=TELEGRAM_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
app = FastAPI()

# --------------------
# Handlers
# --------------------
@dp.message(Command(commands=["start"]))
async def cmd_start(message: Message):
    await message.answer("Olá! Bot funcionando com Webhook 3.x 🟢")

# --------------------
# Webhook endpoint
# --------------------
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(update)  # <-- 3.x usa feed_update
    return {"ok": True}

# --------------------
# Start webhook (apenas para configuração inicial, Telegram precisa do set_webhook)
# --------------------
async def on_startup():
    await bot.delete_webhook()  # remove webhook antigo
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)

@app.on_event("startup")
async def startup_event():
    await on_startup()

# --------------------
# Rodando localmente com Uvicorn (se precisar)
# --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
