from aiogram import Router, types
from aiogram.filters import Command

from utils.create_keyboard import CreateKeyboard

command_router = Router()
cr_kb = CreateKeyboard()


@command_router.message(Command("start"))
async def process_start_command(message: types.Message):
    buttons = ["Статистика", "ПАПКИ/КАНАЛЫ", "Настройки"]
    keyboard = await cr_kb.create_keyboard(buttons)
    start_txt = "Привет"
    await message.answer(start_txt, reply_markup=keyboard)
