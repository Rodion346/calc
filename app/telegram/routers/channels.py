from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
import logging
from core.models.db_helper import db_helper
from core.repositories import ChannelRepository
from telegram.telethon_client import TelegramClientWrapper
from utils.create_keyboard import CreateKeyboard

channel_router = Router()

logger = logging.getLogger(__name__)

folders = ["RF", "DF"]
client_wrapper = TelegramClientWrapper()
channelRepo = ChannelRepository(db_helper.session_getter)


class Form(StatesGroup):
    waiting_for_number = State()


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


@channel_router.callback_query(F.data.startswith("info_"))
async def handle_channel_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    folder_title = callback_query.data[5:]  # Удаляем префикс "kb_"
    channels = await channelRepo.select_channels_by_folder_id(folder_title)
    channels_group_message = ""
    for channel in channels:
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.id} - {channel.channel_name} \n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
    await callback_query.message.edit_text(
        f"Выберите канал:\n{channels_group_message}", reply_markup=None
    )
    await state.clear()
    await state.set_state(Form.waiting_for_number)


@channel_router.message(Form.waiting_for_number)
async def id_channel(message: Message, state: FSMContext):
    await state.clear()
    if message.text.isdigit():
        channels_group_message = ""
        channel = await channelRepo.select_channels_by_row_id(int(message.text))
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        await message.answer(
            f"{channels_group_message}",
            reply_markup=await CreateKeyboard().create_kb_chanel_settings(channel.id),
        )


@channel_router.callback_query(F.data.startswith("set_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    set_title = callback_query.data.split("_")
    if set_title[1] == "active":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "test":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "disable":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])

    channels_group_message = ""
    channel = await channelRepo.select_channels_by_row_id(int(set_title[2]))
    if channel.channel_stats == "active":
        channels_group_message += f"🟢 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
    elif channel.channel_stats == "test":
        channels_group_message += f"🟡 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
    elif channel.channel_stats == "disable":
        channels_group_message += f"🔴 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
    await callback_query.message.edit_text(
        f"{channels_group_message}",
        reply_markup=await CreateKeyboard().create_kb_chanel_settings(channel.id),
    )


@channel_router.message(F.text == "Папки")
async def get_list_channel(message: types.Message):
    folder_list = await client_wrapper.get_folders()
    kb = await CreateKeyboard().create_kb_folders(folder_list)
    await message.answer("Папки:", reply_markup=kb)
