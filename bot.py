from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
import asyncio
import mercadopago
from config import BOT_TOKEN, MP_ACCESS_TOKEN, GROUP_ID
import base64
from fastapi import FastAPI, Request
import uvicorn

# Inicializa bot e dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Inicializa Mercado Pago
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

# Inicializa FastAPI
app = FastAPI()

# /start
@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    await message.answer(
        "👋 Olá!\n\n"
        "💳 Assinatura mensal via Pix\n"
        "Digite /assinar para gerar seu pagamento."
    )

# /assinar
@dp.message(Command(commands=["assinar"]))
async def assinar_handler(message: types.Message):
    user_id = message.from_user.id

    payment_data = {
        "transaction_amount": 1.0,
        "description": "Assinatura Mensal",
        "payment_method_id": "pix",
        "payer": {"email": f"{user_id}@telegram.com"}
    }

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        poi = payment.get("point_of_interaction")
        if poi:
            transaction_data = poi.get("transaction_data", {})
            qr_code = transaction_data.get("qr_code")
            qr_code_base64 = transaction_data.get("qr_code_base64")

            if qr_code and qr_code_base64:
                qr_bytes = base64.b64decode(qr_code_base64)
                qr_file = BufferedInputFile(file=qr_bytes, filename="pix.png")

                await message.answer(f"💳 Pagamento Pix gerado!\n\nCopia e cola: `{qr_code}`", parse_mode="Markdown")
                await message.answer_photo(photo=qr_file, caption="📷 QR Code Pix")
                return

        await message.answer("❌ Erro: não foi possível gerar o QR Code. Tente novamente mais tarde.")

    except Exception as e:
        await message.answer(f"❌ Erro ao gerar Pix: {str(e)}")


# Webhook do Mercado Pago
@app.post("/webhook")
async def mp_webhook(request: Request):
    data = await request.json()
    try:
        status = data.get("data", {}).get("status")
        payer_email = data.get("data", {}).get("payer", {}).get("email")

        if status == "approved" and payer_email:
            user_id_str = payer_email.split("@")[0]
            if user_id_str.isdigit():
                user_id = int(user_id_str)
                await bot.send_message(user_id, "✅ Pagamento confirmado! Você foi adicionado ao grupo.")
                await bot.add_chat_members(chat_id=GROUP_ID, user_ids=[user_id])
                print(f"Usuário {user_id} adicionado ao grupo!")

    except Exception as e:
        print(f"Erro no webhook: {e}")

    return {"status": "ok"}


async def main():
    # Roda FastAPI no mesmo loop usando Uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # roda bot + FastAPI juntos
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())
