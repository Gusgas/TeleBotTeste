# bot.py
import asyncio
import threading
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ===========================
# Configurações do Telegram
# ===========================
TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN"
CHAT_ID = "SEU_CHAT_ID"  # onde as notificações vão chegar

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# ===========================
# Handlers do Telegram
# ===========================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.reply("Bot iniciado! Enviará notificações de pagamentos.")

# ===========================
# FastAPI app para webhooks
# ===========================
app = FastAPI()

@app.post("/webhook")
async def mp_webhook(request: Request):
    data = await request.json()
    print("Recebi notificação do Mercado Pago:", data)

    # Envia mensagem para o Telegram
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"Nova notificação de pagamento:\n{data}"
        )
    except Exception as e:
        print("Erro ao enviar mensagem para Telegram:", e)

    return {"status": "ok"}

# ===========================
# Função para rodar o bot do Telegram
# ===========================
async def start_bot():
    executor.start_polling(dp, skip_updates=True)

# ===========================
# Inicia bot em thread separada
# ===========================
threading.Thread(target=lambda: asyncio.run(start_bot())).start()

# ===========================
# Roda FastAPI com Uvicorn
# ===========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
