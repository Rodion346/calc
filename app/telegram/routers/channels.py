from aiogram import Router, F, types

from core.models.db_helper import db_helper
from core.repositories import ChannelRepository
from telegram.telethon_client import TelegramClientWrapper
from utils.create_keyboard import CreateKeyboard

channel_router = Router()

folders = ["RF", "DF"]
client_wrapper = TelegramClientWrapper()
channelRepo = ChannelRepository(db_helper.session_getter)


@channel_router.message(F.text == "Каналы")
async def get_list_channel(message: types.Message):
    channels_group_message = ""
    count = 0
    channels = await channelRepo.select_all_channels()
    for channel in channels:
        count += 1
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {count} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {count} - {channel.channel_name} \n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {count} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
    await message.answer(f"Выберите канал:\n{channels_group_message}")


@channel_router.callback_query(F.data.startswith("kb_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    channel_title = callback_query.data[3:]  # Удаляем префикс "kb_"
    await callback_query.message.answer(f"Вы выбрали папку: {channel_title}")
    await callback_query.answer()


@channel_router.message(F.text == "Папки")
async def get_list_channel(message: types.Message):
    folder_list = await client_wrapper.get_folders()
    kb = await CreateKeyboard().create_kb_folders(folder_list)
    await message.answer("Папки:", reply_markup=kb)
