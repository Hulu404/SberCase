import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

import io
from gtts import gTTS
from pydub import AudioSegment

from test import response_gigachat

from config import *
from test import *

bot = Bot(token=TOKEN)
dp = Dispatcher()


def text_to_voice(text: str, lang: str = 'ru') -> io.BytesIO:
    # Преобразует текст в голосовое сообщение
    try:
        # Создаем TTS
        tts = gTTS(text=text, lang=lang, slow=False)

        # Сохраняем в MP3
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        # Конвертируем в OGG (Telegram предпочитает OGG)
        audio = AudioSegment.from_mp3(mp3_buffer)
        ogg_buffer = io.BytesIO()
        audio.export(ogg_buffer, format="ogg", codec="libvorbis")
        ogg_buffer.seek(0)

        return ogg_buffer

    except Exception as e:
        logging.error(f"Ошибка TTS: {e}")
        return None

async def send_voice_message(chat_id: int, text: str):
    # Отправляет голосовое сообщение с текстом
    try:
        # Показываем статус записи
        await bot.send_chat_action(chat_id, "record_voice")

        # Преобразуем текст в голос
        voice_buffer = text_to_voice(text)

        if voice_buffer:
            # Отправляем голосовое сообщение
            await bot.send_voice(
                chat_id=chat_id,
                voice=types.BufferedInputFile(
                    voice_buffer.getvalue(),
                    filename="voice.ogg"
                ),
                caption=text[:100] + ("..." if len(text) > 100 else "")
            )
            return True
        else:
            await bot.send_message(chat_id, "Ошибка преобразования текста в речь")
            return False

    except Exception as e:
        logging.error(f"Ошибка отправки: {e}")
        await bot.send_message(chat_id, "Произошла ошибка")
        return False



@dp.message(Command('start'))
async def start_message(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\nРасскажи, как ты себя чувствуешь?")

@dp.message(F.text)
async def text_message(message: types.Message):
    gigachat_response = response_gigachat(message.text)   # Запрос к гигачату
    await message.answer(gigachat_response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")