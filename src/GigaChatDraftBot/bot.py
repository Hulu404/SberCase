import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

#from text_to_speech import voice_to_text

from config import *
from test import *

bot = Bot(token=TOKEN)
dp = Dispatcher()



@dp.message(Command('start'))
async def start_message(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}!\nЯ **Ника**, твой ИИ-помощник для ментальной поддержки в спорте.\n"
                         f"Расскажи, с каким вызовом столкнулся на этой неделе?\n\n"
                         f"*Как ИИ, я не заменяю работу с психологом, но я всегда здесь, чтобы выслушать и предложить практическую стратегию.*")

@dp.message(F.text)
async def text_message(message: types.Message):
    # Отправляем уведомление о начале обработки - в дальнейшем будем его изменять
    notice_msg = await message.answer("⌛️ Начинаю обрабатывать ваш запрос...")
    await bot.send_chat_action(message.chat.id, "typing")

    gigachat_response = response_gigachat(message.text)   # Запрос к гигачату

    # Удаляем уведомление и отправляем финальный ответ
    await notice_msg.delete()
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