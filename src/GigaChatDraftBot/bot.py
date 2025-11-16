import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

import io
from gtts import gTTS

from test import response_gigachat
from text_to_speech import voice_to_text

from config import *
from test import *

bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(Command('start'))
async def start_message(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\nРасскажи, как ты себя чувствуешь?")

@dp.message(F.text)
async def text_message(message: types.Message):
    gigachat_response = response_gigachat(message.text)   # Запрос к гигачату
    await message.answer(gigachat_response)

@dp.message(F.voice)
async def voice_message(message: types.Message):
    pass



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")