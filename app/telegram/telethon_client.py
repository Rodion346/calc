import json
import logging
from telethon import TelegramClient, events
from telethon.errors import ChannelPrivateError
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import (
    InputPeerEmpty,
    DialogFilter,
    InputPeerChannel,
    PeerChannel,
)
from core.repositories.folder import FolderRepository
from core.repositories.channel import ChannelRepository
from core.models.db_helper import db_helper
from core.repositories import SignalRepository
from utils.AI_chat import AI
from datetime import datetime
import asyncio

from utils.create_templates import format_message

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

channelRepo = ChannelRepository(db_helper.session_getter)
folderRepo = FolderRepository(db_helper.session_getter)
signalRepo = SignalRepository(db_helper.session_getter)


class TelegramClientWrapper:
    def __init__(
        self,
        api_id=23069367,
        api_hash="cdc1df657033fc09cdf875fe4c029708",
        session_name="session",
        destination_channel_id=--1002112786462,
        system_version="4.16.30-vxCUSTOM",
    ):
        """Инициализация TelegramClientWrapper."""
        self.client = TelegramClient(
            session_name, api_id, api_hash, system_version=system_version
        )
        self.destination_channel_id = destination_channel_id
        self.source_channel_id = []
        logger.info("Инициализация TelegramClientWrapper завершена.")

    async def start(self):
        """Запуск Telegram клиента."""
        logger.info("Запуск Telegram клиента.")
        await self.client.start()
        await self.update_channels()
        asyncio.create_task(self.periodic_update_channels())
        logger.info("Telegram клиент запущен.")

    async def stop(self):
        """Остановка Telegram клиента."""
        logger.info("Остановка Telegram клиента.")
        await self.client.disconnect()
        logger.info("Telegram клиент остановлен.")

    async def get_folders(self):
        """Получение списка папок (фильтров диалогов)."""
        logger.info("Начало получения списка папок.")
        result = await self.client(GetDialogFiltersRequest())
        folders = []
        for folder in result.filters:
            if isinstance(folder, DialogFilter):
                folders.append(folder)
        logger.info("Получение списка папок завершено.")
        return folders

    async def check_and_add_channel(self):
        folders_name = []
        list_channel = []
        for i in await folderRepo.select_all_active_folders():
            folders_name.append(i.folder_title)
        folders = await self.get_folders()
        for folder in folders:
            if folder.title in folders_name:
                for entity in folder.include_peers:
                    entity_info = await self.client.get_input_entity(entity)
                    logger.info(f"{entity_info}")
                    try:
                        entity_info = await self.client.get_entity(
                            entity_info.channel_id
                        )
                        await channelRepo.add_channel(entity_info, folder.title)
                    except ChannelPrivateError:
                        print(
                            "Ошибка: нет доступа к каналу. Возможно, вы забанены или канал частный."
                        )
        await folderRepo.add_folders(folders)

        for i in await folderRepo.select_all_folders():
            folders_name.append(i.folder_title)
        folders = await self.get_folders()
        for folder in folders:
            if folder.title in folders_name:
                for entity in folder.include_peers:
                    entity_info = await self.client.get_input_entity(entity)
                    if isinstance(entity_info, InputPeerChannel):
                        list_channel.append(int(entity.channel_id))
        channels = await channelRepo.select_all_channels()
        for channel in channels:
            if int(channel.channel_id) not in list_channel:
                await channelRepo.delete_channel(str(channel.channel_id))

    async def get_channel_in_folders(self, folder_names):
        """Получение каналов в указанных папках."""
        logger.info(f"Начало получения каналов в папках: {folder_names}.")
        folders = await self.get_folders()
        channels = []
        for folder in folders:
            if folder.title in folder_names:
                for entity in folder.include_peers:
                    entity_info = await self.client.get_input_entity(entity)
                    if hasattr(entity_info, "megagroup") or hasattr(
                        entity_info, "broadcast"
                    ):
                        channels.append(entity_info)
        logger.info(f"Получение каналов в папках завершено: {folder_names}.")
        return channels

    async def update_channels(self):
        active_folders = await folderRepo.select_all_active_folders()
        all_channel = await channelRepo.select_all_channels()
        await self.check_and_add_channel()
        self.source_channel_id = []
        for folder in active_folders:
            for channel in all_channel:
                if (
                    folder.folder_title == channel.folder_id
                    and channel.channel_stats == "active"
                ):
                    self.source_channel_id.append(int("-100" + str(channel.channel_id)))

        # Обновляем обработчики событий
        self.update_event_handlers()

    async def periodic_update_channels(self):
        while True:
            await asyncio.sleep(60)  # Обновляем каждые 60 секунд
            await self.update_channels()

    def update_event_handlers(self):
        # Удаляем старые обработчики
        self.client.remove_event_handler(self.handler)

        # Добавляем новые обработчики
        self.client.on(events.NewMessage(chats=self.source_channel_id))(self.handler)

    async def handler(self, event):
        # Пересылаем сообщение в целевой канал
        text_dict = await AI(event.message.text)
        if text_dict == "False":
            await self.client.send_message(
                self.destination_channel_id,
                event.message.text
                + "\n\n"
                + "Это не сигнал и в активных каналах его не будет",
            )
            return
        elif (
            (text_dict["Coin"] is None)
            or (text_dict["Trand"] is None)
            or (
                (text_dict["Entrance_point_tvh"] is None)
                and (text_dict["Entrance_point_lvh"] is None)
            )
            or (text_dict["Take_profit"] is None)
        ):
            await self.client.send_message(
                self.destination_channel_id,
                event.message.text
                + "\n\n"
                + "Это не сигнал и в активных каналах его не будет",
            )
            return

        channelInfo = await self.client.get_entity(event.chat_id)
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        # Добавляем новые ключи и значения
        text_dict["channel_id"] = channelInfo.id
        text_dict["message_id"] = event.id
        text_dict["channel_name"] = channelInfo.title
        text_dict["date"] = date
        text_dict["time"] = time

        # text_dict = json.dumps(text_dict)

        # Преобразуем обновленный объект обратно в JSON-строку

        await self.client.send_message(
            self.destination_channel_id,
            event.message.text + "\n\n" + format_message(text_dict),
            parse_mode="html",
        )

    async def siclesa(self):
        """Отслеживание новых сообщений в исходном канале и пересылка их в целевой канал."""
        logger.info("Начало отслеживания новых сообщений.")
        await self.client.run_until_disconnected()


client_wrapper = TelegramClientWrapper()


async def main():
    await client_wrapper.stop()


# Запускаем асинхронную функцию
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


"""async def main():
    # ID каналов (замените на свои значения)
    source_channel_id = []  # ID исходного канала
    destination_channel_id = -1002498219342  # ID целевого канала
    active_folders = await folderRepo.select_all_active_folders()
    all_channel = await channelRepo.select_all_channels()
    for folder in active_folders:
        for channel in all_channel:
            if (
                folder.folder_title == channel.folder_id
                and channel.channel_stats == "active"
            ):
                source_channel_id.append(int("-100" + str(channel.channel_id)))

    await client_wrapper.siclesa(source_channel_id, destination_channel_id)"""


"""async def main():
    wrapper = TelegramClientWrapper()
    await wrapper.start()
    fold = []
    active_folders = await folderRepo.select_all_active_folders()
    for i in active_folders:
        fold.append(i.folder_title)

    a = await wrapper.get_folders()
    for i in a:
        print(i)
"""
