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
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nЯ **Ника**, твой ИИ-помощник для ментальной поддержки в спорте.\n"
        f"Расскажи, с каким вызовом столкнулся на этой неделе?\n\n"
        f"*Как ИИ, я не заменяю работу с психологом, но я всегда здесь, чтобы выслушать и предложить практическую стратегию.*",
    parse_mode='MarkdownV2')


@dp.message(F.voice)
async def send_voi(message: types.Message):
    # Отправляем уведомление о начале обработки - в дальнейшем будем его изменять
    notice_msg = await message.answer("🎧 Начинаю обрабатывать голосовое сообщение...")
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        # Скачиваем голосовое сообщение
        voice_file = await bot.get_file(message.voice.file_id)
        voice_data = await bot.download_file(voice_file.file_path)

        # Преобразуем в текст
        text = await speech_processor.speech_to_text(voice_data.read())

        if text:
            # Отправка распознанного текста
            await message.answer(f"🎤 Распознано: {text}")

            # Обновляем уведомление для этапа нейросети
            await notice_msg.edit_text("⌛️ Начинаю обрабатывать ваш запрос...")
            await bot.send_chat_action(message.chat.id, "typing")

            # Отправляем в GigaChat
            response = response_gigachat(text)

            # Удаляем уведомление и отправляем финальный ответ
            await notice_msg.delete()
            await message.answer(response)
        else:
            await message.answer("Не удалось распознать голос")
            await notice_msg.delete()
    except Exception as e:
        await notice_msg.delete()
        await message.answer("❌ Произошла ошибка при обработке аудио")
        print(f"[INFO]: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")