import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import *
# from test import *

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_message(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\nРасскажи, как ты себя чувствуешь?")

@dp.message()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")