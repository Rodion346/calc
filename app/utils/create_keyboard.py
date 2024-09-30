import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from core.models.db_helper import db_helper
from core.repositories import ChannelRepository, FolderRepository

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

channelRepo = ChannelRepository(db_helper.session_getter)
folderRepo = FolderRepository(db_helper.session_getter)


class CreateKeyboard:
    def __init__(self):
        """Инициализация класса CreateKeyboard."""
        pass

    async def create_keyboard(self, buttons, columns=2):
        """Создание клавиатуры с кнопками."""
        logger.info("Начало создания клавиатуры с кнопками.")
        keyboard_buttons = []
        for i in range(0, len(buttons), columns):
            row = [
                types.KeyboardButton(text=button) for button in buttons[i : i + columns]
            ]
            keyboard_buttons.append(row)
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=keyboard_buttons, resize_keyboard=True
        )
        logger.info("Создание клавиатуры с кнопками завершено.")
        return keyboard

    async def create_kb_channel(self, folders, row=1):
        """Создание инлайн-клавиатуры для каналов."""
        logger.info("Начало создания инлайн-клавиатуры для каналов.")
        k_b = InlineKeyboardBuilder()
        for i in range(0, len(folders), row):
            row_buttons = [
                InlineKeyboardButton(
                    text=folder.title,
                    callback_data=f"kb_{folder.title}",
                )
                for folder in folders[i : i + row]
            ]
            k_b.row(*row_buttons)
        keyboard = k_b.as_markup()
        logger.info("Создание инлайн-клавиатуры для каналов завершено.")
        return keyboard

    async def create_kb_folders(self, folders, row=1):
        """Создание инлайн-клавиатуры для папок."""
        logger.info("Начало создания инлайн-клавиатуры для папок.")
        k_b = InlineKeyboardBuilder()
        butt_all = InlineKeyboardButton(text="ALL", callback_data="info_ALL")
        k_b.add(butt_all)
        for i in range(0, len(folders), row):
            row_buttons = []
            for folder in folders[i : i + row]:
                stats_folder = (
                    await folderRepo.select_folder_by_id(str(folder.id))
                ).folder_status
                channels = await channelRepo.select_channels_by_folder_id(folder.title)
                active_channels, test_channels, inactive_channels = 0, 0, 0
                for channel in channels:
                    if channel.channel_stats == "active":
                        active_channels += 1
                    elif channel.channel_stats == "test":
                        test_channels += 1
                    elif channel.channel_stats == "disable":
                        inactive_channels += 1
                info_button = InlineKeyboardButton(
                    text=f"{'🔓' if stats_folder == 'active' else '🔐'}   {folder.title}   ||  🟢 - {active_channels} 🟡 - {test_channels} 🔴 - {inactive_channels}",
                    callback_data=f"info_{folder.title}",
                )
                row_buttons.extend([info_button])
            k_b.row(*row_buttons)
        keyboard = k_b.as_markup()
        logger.info("Создание инлайн-клавиатуры для папок завершено.")
        return keyboard

    async def create_kb_chanel_settings(self, channel_id, f_title):
        """Создание инлайн-клавиатуры для настроек канала."""
        logger.info("Начало создания инлайн-клавиатуры для настроек канала.")
        kb_builder = InlineKeyboardBuilder()
        button1 = InlineKeyboardButton(
            text="🟢 Активировать", callback_data=f"set_active_{channel_id}_{f_title}"
        )
        kb_builder.add(button1)
        button2 = InlineKeyboardButton(
            text="🟡 Тестировать", callback_data=f"set_test_{channel_id}_{f_title}"
        )
        kb_builder.add(button2)
        button3 = InlineKeyboardButton(
            text="🔴 Деактивировать",
            callback_data=f"set_disable_{channel_id}_{f_title}",
        )
        kb_builder.add(button3)
        keyboard = kb_builder.as_markup()
        logger.info("Создание инлайн-клавиатуры для настроек канала завершено.")
        return keyboard

    async def state_folder(self, stats, title=""):
        """Создание инлайн-клавиатуры для изменения статуса папки."""
        logger.info("Начало создания инлайн-клавиатуры для изменения статуса папки.")
        kb_builder = InlineKeyboardBuilder()
        if stats == "disable":
            button1 = InlineKeyboardButton(
                text="ON", callback_data=f"folder_on_{title}"
            )
            kb_builder.add(button1)
        else:
            button2 = InlineKeyboardButton(
                text="OFF", callback_data=f"folder_off_{title}"
            )
            kb_builder.add(button2)

        keyboard = kb_builder.as_markup()
        logger.info("Создание инлайн-клавиатуры для изменения статуса папки завершено.")
        return keyboard
