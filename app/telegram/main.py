import asyncio
import logging

from aiogram import Dispatcher, Bot

from telegram.routers.channels import channel_router
from telegram.routers.commands import command_router

dp = Dispatcher()
bot = Bot(token="6830235739:AAG0Bo5lnabU4hDVWlhPQmLtiMVePI2xRGg")

dp.include_router(command_router)
dp.include_router(channel_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
