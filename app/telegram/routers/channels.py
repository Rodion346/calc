from aiogram import Router, F, types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
import logging
from core.models.db_helper import db_helper
from core.repositories import ChannelRepository, FolderRepository

from telegram.telethon_client import TelegramClientWrapper
from utils.create_keyboard import CreateKeyboard

channel_router = Router()

logger = logging.getLogger(__name__)

folders = ["RF", "DF"]
client_wrapper = TelegramClientWrapper()
channelRepo = ChannelRepository(db_helper.session_getter)
folderRepo = FolderRepository(db_helper.session_getter)
bot = Bot(token="6830235739:AAG0Bo5lnabU4hDVWlhPQmLtiMVePI2xRGg")


class Form(StatesGroup):
    waiting_for_number = State()
    waiting_folder_title = ""
    waiting_message_id = 0
    waiting_callback_id = ""


@channel_router.callback_query(F.data.startswith("info_"))
async def handle_channel_selection(
    callback_query: types.CallbackQuery, state: FSMContext
):
    Form.waiting_callback_id = callback_query.id
    folder_title = callback_query.data[5:]  # Удаляем префикс "kb_"
    channels = await channelRepo.select_channels_by_folder_id(folder_title)
    channels = sorted(channels, key=lambda channel: channel.id)
    channels_group_message = f"Список каналов в папке - {folder_title}\n\n"
    for channel in channels:
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.id} - {channel.channel_name} \n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
    await callback_query.message.edit_text(
        f"{channels_group_message}\n Выберите канал:",
        reply_markup=await CreateKeyboard().state_folder(
            (await folderRepo.select_folder_by_title(folder_title)).folder_status,
            folder_title,
        ),
    )
    await state.set_state(Form.waiting_for_number)
    Form.waiting_folder_title = folder_title
    Form.waiting_message_id = callback_query.message.message_id


@channel_router.message(Form.waiting_for_number)
async def id_channel(message: Message, state: FSMContext):
    if message.text.isdigit():
        channels_group_message = (
            f"Список каналов в папке - {Form.waiting_folder_title}\n\n"
        )
        channel = await channelRepo.select_channels_by_row_id(int(message.text))
        if (
            channel.channel_stats == "active"
            and channel.folder_id == Form.waiting_folder_title
        ):
            channels_group_message += f"🟢 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        elif (
            channel.channel_stats == "test"
            and channel.folder_id == Form.waiting_folder_title
        ):
            channels_group_message += f"🟡 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        elif (
            channel.channel_stats == "disable"
            and channel.folder_id == Form.waiting_folder_title
        ):
            channels_group_message += f"🔴 {channel.channel_name}\nID: {channel.channel_id}"  # назначение списка переменной: статус, номер, имя канала
        else:
            await bot.answer_callback_query(
                Form.waiting_callback_id, show_alert=True, text="Ошибка"
            )
            return
        await message.answer(
            f"{channels_group_message}",
            reply_markup=await CreateKeyboard().create_kb_chanel_settings(
                channel.id, Form.waiting_folder_title
            ),
        )
    else:
        await state.clear()
        if message.text == "ПАПКИ/КАНАЛЫ":
            await get_list_channel(message)
        elif message.text == "Статистика":
            pass


@channel_router.callback_query(F.data.startswith("set_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    set_title = callback_query.data.split("_")
    if set_title[1] == "active":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "test":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "disable":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])

    await callback_query.message.delete()

    channels = await channelRepo.select_channels_by_folder_id(set_title[3])
    channels = sorted(channels, key=lambda channel: channel.id)
    channels_group_message = f"Список каналов в папке - {Form.waiting_folder_title}\n\n"
    for channel in channels:
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.id} - {channel.channel_name} \n"  # назначение списка переменной: статус, номер, имя канала
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.id} - {channel.channel_name}\n"  # назначение списка переменной: статус, номер, имя канала

    await bot.edit_message_text(
        channels_group_message,
        chat_id=callback_query.from_user.id,
        message_id=Form.waiting_message_id,
        reply_markup=await CreateKeyboard().state_folder(
            (await folderRepo.select_folder_by_title(set_title[3])).folder_status,
            set_title[3],
        ),
    )


@channel_router.callback_query(F.data.startswith("folder_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    set_stats = callback_query.data.split("_")
    if set_stats[1] == "off":
        await folderRepo.update_stats_folder(set_stats[2], "disable")
        await callback_query.message.edit_reply_markup(
            reply_markup=await CreateKeyboard().state_folder(
                (await folderRepo.select_folder_by_title(set_stats[2])).folder_status,
                set_stats[2],
            )
        )
    else:
        await folderRepo.update_stats_folder(set_stats[2], "active")
        await callback_query.message.edit_reply_markup(
            reply_markup=await CreateKeyboard().state_folder(
                (await folderRepo.select_folder_by_title(set_stats[2])).folder_status,
                set_stats[2],
            )
        )


@channel_router.message(F.text == "ПАПКИ/КАНАЛЫ")
async def get_list_channel(message: types.Message):
    folder_list = await client_wrapper.get_folders()
    kb = await CreateKeyboard().create_kb_folders(folder_list)
    await message.answer("Папки:", reply_markup=kb)
