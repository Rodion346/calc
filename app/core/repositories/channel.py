import logging
from contextlib import asynccontextmanager

from sqlalchemy import update, delete
from sqlalchemy.future import select
from ..models.channel import Channel
from ..models.db_helper import db_helper

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ChannelRepository:
    def __init__(self, db):
        self.db = db
        logger.info("Инициализация ChannelRepository с базой данных.")

    async def select_all_channels(self):
        """Получение всех каналов из базы данных."""
        async with self.db() as session:
            logger.info("Начало выполнения запроса для получения всех каналов.")
            result = await session.execute(select(Channel).order_by(Channel.id))
            channels = result.scalars().all()
            logger.info("Получены все каналы из базы данных.")
            return channels

    async def add_channel(self, channel, folder_id):
        """Добавление нового канала в базу данных."""
        async with self.db() as session:
            try:
                logger.info(f"Проверка существования канала с channel_id={channel.id}.")
                result = await session.execute(select(Channel).filter_by(channel_id=str(channel.id)))
                existing_channel = result.scalars().first()

                if existing_channel:
                    logger.warning(f"Канал с channel_id={channel.id} уже существует.")
                    return

                new_channel = Channel(
                    folder_id=folder_id,
                    channel_id=str(channel.id),
                    channel_name=channel.title,
                    channel_stats="test",
                    access_hash=str(channel.access_hash),
                )
                session.add(new_channel)
                await session.commit()
                logger.info(f"Канал {channel.title} добавлен в базу данных.")

            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при добавлении канала {channel.title}: {e}")
                return f"Ошибка. Проблема с запросом в базу данных _ add channel.\n{e}"
        return "True"

    async def select_channels_by_id(self, channel_id):
        """Получение канала по ID."""
        async with self.db() as session:
            logger.info(f"Начало выполнения запроса для получения канала с ID {channel_id}.")
            result = await session.execute(
                select(Channel).filter(Channel.channel_id == channel_id)
            )
            channel = result.scalars().first()
            logger.info(f"Получен канал с ID {channel_id}.")
            return channel

    async def select_channels_by_row_id(self, id):
        """Получение канала по ID строки."""
        async with self.db() as session:
            logger.info(f"Начало выполнения запроса для получения канала с ID строки {id}.")
            result = await session.execute(select(Channel).filter(Channel.id == id))
            channel = result.scalars().first()
            logger.info(f"Получен канал с ID строки {id}.")
            return channel

    async def select_channels_by_folder_id(self, folder_id):
        """Получение каналов по ID папки."""
        async with self.db() as session:
            logger.info(f"Начало выполнения запроса для получения каналов для папки с ID {folder_id}.")
            result = await session.execute(
                select(Channel).filter(Channel.folder_id == folder_id)
            )
            channels = result.scalars().all()
            logger.info(f"Получены каналы для папки с ID {folder_id}.")
            return channels

    async def update_stats_channel(self, channel_id, stats):
        async with self.db() as session:
            logger.info(f"Начало выполнения запроса для обновления статуса канала с ID {channel_id}.")
            await session.execute(
                update(Channel).where(Channel.id == channel_id).values(channel_stats=stats))
            await session.commit()
            logger.info(f"Обновлен статус канала с ID {channel_id}.")

    async def delete_channel(self, channel_id):
        async with self.db() as session:
            logger.info(f"Начало выполнения запроса для удаления канала с ID {channel_id}.")
            await session.execute(
                delete(Channel).where(Channel.channel_id == str(channel_id))
            )
            await session.commit()
            logger.info(f"Канал с ID {channel_id} удален.")
