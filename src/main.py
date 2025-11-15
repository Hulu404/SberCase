import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from neural_api_async import AsyncNeuralApi
from src.GigaChatDraftBot.config import token

bot = Bot(token=token)
dp = Dispatcher(bot=bot)
router = Router()
dp.include_router(router)

neural_api = AsyncNeuralApi()


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")