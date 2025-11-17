import asyncio
import logging
#final
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from test import response_gigachat

from handlers.keyboards import options
from GigaChatDraftBot.config import *
from test import *

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_message(message: types.Message):
    TEXT = """
    Меня зовут Ника! Я твоя ИИ-помощница!
        Я могу помочь вам:

        Выразить и проанализировать свои эмоции.
        Провести сессию осознанности или дыхательное упражнение.
        Проработать тревожные мысли.
        Зафиксировать ваши успехи и благодарность.

    Я — программа, а не живой психолог. Моя задача — предоставить вам инструменты для самопомощи.
    """
    await message.answer(f"Привет, {message.from_user.first_name}!{TEXT}")



@dp.message(F.text)
async def text_message(message: types.Message):
    gigachat_response = await response_gigachat(message.text)   # Запрос к гигачату
    await message.answer(gigachat_response)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")