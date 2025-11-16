import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from src.GigaChatDraftBot.test import response_gigachat
from text_to_speech2 import *
from config import TOKEN, YANDEX_API_KEY


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_message(message: types.Message):
    await message.answer("Ghngjjsn")


@dp.message(F.voice)
async def send_voi(message: types.Message):
    await bot.send_chat_action(message.chat.id, "typing")

    await bot.send_chat_action(message.chat.id, "typing")

    try:
        # Скачиваем голосовое сообщение
        voice_file = await bot.get_file(message.voice.file_id)
        voice_data = await bot.download_file(voice_file.file_path)

        # Преобразуем в текст
        text = await speech_processor.speech_to_text(voice_data.read())

        if text:
            await message.answer(f"🎤 Распознано: {text}")

            # Отправляем в GigaChat
            await bot.send_chat_action(message.chat.id, "typing")
            response = response_gigachat(message.text)
            await message.answer(response)
        else:
            await message.answer("Не удалось распознать голос")

    except Exception as e:
        print(f"[INFO]: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")