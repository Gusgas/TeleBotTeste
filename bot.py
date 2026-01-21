# bot.py
import asyncio
import threading
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types

# ===========================
# Configurações do Telegram
# ===========================
TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN"
CHAT_ID = "SEU_CHAT_ID"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# ===========================
# Handlers do Telegram
# ===========================
@dp.message()
async def handle_message(message: types.Message):
    if message.text == "/start":
        await message.answer("Bot iniciado! Enviará notificações de pagamentos.")

# ===========================
# FastAPI app para webhooks
# ===========================
app = FastAPI()

@app.post("/webhook")
async def mp_webhook(request: Request):
    data = await request.json()
    print("Recebi notificação do Mercado Pago:", data)

    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"Nova notificação de pagamento:\n{data}"
        )
    except Exception as e:
        print("Erro ao enviar mensagem para Telegram:", e)

    return {"status": "ok"}

# ===========================
# Função para rodar o bot
# ===========================
async def start_bot():
    # Conecta o bot ao Dispatcher
    dp.startup.register(lambda _: print("Bot do Telegram iniciado!"))
    # Start polling
    await dp.start_polling(bot)

# ===========================
# Rodar bot em thread separada
# ===========================
threading.Thread(target=lambda: asyncio.run(start_bot()), daemon=True).start()

# ===========================
# Roda FastAPI com Uvicorn
# ===========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
