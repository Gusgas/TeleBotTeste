import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import mercadopago
import asyncio

# -----------------------------
# Configurações
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")  # Mercado Pago
WEBHOOK_BASE = os.getenv("WEBHOOK_BASE")  # Ex: https://seuapp.onrender.com

if not TELEGRAM_TOKEN or not MP_ACCESS_TOKEN or not WEBHOOK_BASE:
    raise Exception("Variáveis TELEGRAM_TOKEN, MP_ACCESS_TOKEN ou WEBHOOK_BASE não estão configuradas.")

WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_BASE}{WEBHOOK_PATH}"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
app = FastAPI()

mp = mercadopago.SDK(MP_ACCESS_TOKEN)

# -----------------------------
# Comandos do bot
# -----------------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Olá! Bot funcionando ✅\nEnvie /pay para testar pagamento.")

@dp.message(Command("pay"))
async def cmd_pay(message: types.Message):
    # Exemplo simples: cria uma preferência de pagamento no Mercado Pago
    preference_data = {
        "items": [
            {
                "title": "Teste de Produto",
                "quantity": 1,
                "unit_price": 10.0
            }
        ],
        "payer": {
            "email": "teste@teste.com"
        }
    }
    preference = mp.preference().create(preference_data)
    payment_url = preference["response"]["init_point"]
    await message.answer(f"Clique para pagar: {payment_url}")

# -----------------------------
# Webhook do Telegram
# -----------------------------
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

# -----------------------------
# Webhook do Mercado Pago
# -----------------------------
@app.post("/mp_webhook")
async def mp_webhook(request: Request):
    data = await request.json()
    # Exemplo simples: verifica se o pagamento foi aprovado
    if "type" in data and data["type"] == "payment":
        payment_info = mp.payment().get(data["data"]["id"])
        status = payment_info["response"]["status"]
        payer_email = payment_info["response"]["payer"]["email"]
        if status == "approved":
            # Aqui você pode enviar mensagem para usuário ou registrar no DB
            await bot.send_message(chat_id=payer_email, text="Pagamento aprovado! ✅")
    return {"ok": True}

# -----------------------------
# Inicialização
# -----------------------------
async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook configurado em: {WEBHOOK_URL}")

async def on_shutdown():
    await bot.delete_webhook()

if __name__ == "__main__":
    import uvicorn
    asyncio.run(on_startup())
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
