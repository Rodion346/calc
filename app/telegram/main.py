import asyncio
import logging
import signal

from aiogram import Dispatcher, Bot

from telegram.routers.channels import channel_router, client_wrapper, bot
from telegram.routers.commands import command_router

dp = Dispatcher()


dp.include_router(command_router)
dp.include_router(channel_router)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        await client_wrapper.start()
        await dp.start_polling(bot)
    finally:
        await client_wrapper.stop()


if __name__ == "__main__":
    asyncio.run(main())
