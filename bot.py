import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Pega o token das variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Se não encontrar o token, encerra o bot com erro
if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ Token do Telegram não encontrado! Configure a variável TELEGRAM_TOKEN no Render.")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Comando /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Olá! Bot funcionando ✅")

# Aqui você coloca seus handlers de pagamento ou outros comandos
# Exemplo: Webhook de pagamento Mercado Pago
# async def pagamento_handler(data):
#     ...

if __name__ == "__main__":
    import asyncio
    from aiogram import F
    
    print("Bot iniciado com sucesso!")
    asyncio.run(dp.start_polling(bot))
