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

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    """Обработка выбора канала."""
    logger.info("Начало обработки выбора канала.")
    Form.waiting_callback_id = callback_query.id
    folder_title = callback_query.data[5:]  # Удаляем префикс "info_"
    if folder_title == "ALL":
        channels = await channelRepo.select_all_channels()
    else:
        channels = await channelRepo.select_channels_by_folder_id(folder_title)
    channels = sorted(channels, key=lambda channel: channel.id)
    channels_group_message = f"Список каналов в папке - {folder_title}\n\n"
    for channel in channels:
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.id} - {channel.channel_name}\n"
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.id} - {channel.channel_name} \n"
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.id} - {channel.channel_name}\n"

    if folder_title != "ALL":
        await callback_query.message.edit_text(
            f"{channels_group_message}\n Выберите канал:",
            reply_markup=await CreateKeyboard().state_folder(
                (await folderRepo.select_folder_by_title(folder_title)).folder_status,
                folder_title,
            ),
        )
    else:
        await callback_query.message.edit_text(
            f"{channels_group_message}\n Выберите канал:",
        )
    await state.set_state(Form.waiting_for_number)
    Form.waiting_folder_title = folder_title
    Form.waiting_message_id = callback_query.message.message_id
    logger.info(f"Обработка выбора канала завершена для папки {folder_title}.")


@channel_router.message(Form.waiting_for_number)
async def id_channel(message: Message, state: FSMContext):
    """Обработка ввода ID канала."""
    logger.info("Начало обработки ввода ID канала.")
    if message.text.isdigit():
        channels_group_message = (
            f"Список каналов в папке - {Form.waiting_folder_title}\n\n"
        )
        channel = await channelRepo.select_channels_by_row_id(int(message.text))
        if channel is None:
            await bot.answer_callback_query(
                Form.waiting_callback_id, show_alert=True, text="Нет такого id"
            )
            return
        elif channel.channel_stats == "active" and (
            channel.folder_id == Form.waiting_folder_title
            or Form.waiting_folder_title == "ALL"
        ):
            channels_group_message += (
                f"🟢 {channel.channel_name}\nID: {channel.channel_id}"
            )
        elif channel.channel_stats == "test" and (
            channel.folder_id == Form.waiting_folder_title
            or Form.waiting_folder_title == "ALL"
        ):
            channels_group_message += (
                f"🟡 {channel.channel_name}\nID: {channel.channel_id}"
            )
        elif channel.channel_stats == "disable" and (
            channel.folder_id == Form.waiting_folder_title
            or Form.waiting_folder_title == "ALL"
        ):
            channels_group_message += (
                f"🔴 {channel.channel_name}\nID: {channel.channel_id}"
            )
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
    logger.info("Обработка ввода ID канала завершена.")


@channel_router.callback_query(F.data.startswith("set_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    """Обработка изменения статуса канала."""
    logger.info("Начало обработки изменения статуса канала.")
    set_title = callback_query.data.split("_")
    if set_title[1] == "active":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "test":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])
    elif set_title[1] == "disable":
        await channelRepo.update_stats_channel(int(set_title[2]), set_title[1])

    await callback_query.message.delete()

    if set_title[3] == "ALL":
        channels = await channelRepo.select_all_channels()
    else:
        channels = await channelRepo.select_channels_by_folder_id(set_title[3])
    channels = sorted(channels, key=lambda channel: channel.id)
    channels_group_message = f"Список каналов в папке - {Form.waiting_folder_title}\n\n"
    for channel in channels:
        if channel.channel_stats == "active":
            channels_group_message += f"🟢 {channel.id} - {channel.channel_name}\n"
        elif channel.channel_stats == "test":
            channels_group_message += f"🟡 {channel.id} - {channel.channel_name} \n"
        elif channel.channel_stats == "disable":
            channels_group_message += f"🔴 {channel.id} - {channel.channel_name}\n"

    if set_title[3] == "ALL":
        await bot.edit_message_text(
            channels_group_message + "\nВыберите канал",
            chat_id=callback_query.from_user.id,
            message_id=Form.waiting_message_id,
        )
    else:
        await bot.edit_message_text(
            channels_group_message + "\nВыберите канал",
            chat_id=callback_query.from_user.id,
            message_id=Form.waiting_message_id,
            reply_markup=await CreateKeyboard().state_folder(
                (await folderRepo.select_folder_by_title(set_title[3])).folder_status,
                set_title[3],
            ),
        )
    logger.info("Обработка изменения статуса канала завершена.")


@channel_router.callback_query(F.data.startswith("folder_"))
async def handle_channel_selection(callback_query: types.CallbackQuery):
    """Обработка изменения статуса папки."""
    logger.info("Начало обработки изменения статуса папки.")
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
    logger.info("Обработка изменения статуса папки завершена.")


@channel_router.message(F.text == "ПАПКИ/КАНАЛЫ")
async def get_list_channel(message: types.Message):
    """Получение списка папок/каналов."""
    logger.info("Начало получения списка папок/каналов.")
    folder_list = await client_wrapper.get_folders()
    kb = await CreateKeyboard().create_kb_folders(folder_list)
    await message.answer("Папки:", reply_markup=kb)
    logger.info("Получение списка папок/каналов завершено.")
