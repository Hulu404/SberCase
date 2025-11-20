import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message

from giga_start import *
#final

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
@dp.message(F.text=='/start')
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

# Обработка текстового сообщения
@dp.message(F.text)
async def text_message(message: types.Message):
    gigachat_response = response_gigachat(message.text)   # Запрос к гигачату
    await message.answer(gigachat_response)

### Обработка голосовых сообщений
async def download_voice_to_file(bot: Bot, message: Message, filename="voice_messages_download/temp_voice"):
    """Загрузка голосового сообщения из Телеграм в локальный файл"""
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, destination=f"{filename}.ogg")
    return f"{filename}.ogg"

@dp.message(F.voice)
async def voice_message_handler(message: types.Message, bot: Bot):
    """Распознавание речи и ответ ГигаЧата"""
    try:
        # Скачиваем голосовое сообщение в файл
        filename = await download_voice_to_file(bot, message)
        # Распознаём речь из файла
        text_from_voice = await recognize_speech(filename)
        # Получаем ответ от GigaChat
        gigachat_response = await asyncio.to_thread(response_gigachat, text_from_voice)
        # Отвечаем пользователю текстом
        await message.answer(gigachat_response)

    except Exception as e:
        logging.error(f"Ошибка при обработке голосового сообщения: {e}")
        await message.reply("Возникла ошибка при обработке вашего голосового сообщения.")


async def main():
    await dp.start_polling(bot)
    # await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")