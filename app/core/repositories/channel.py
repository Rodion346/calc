import logging
from sqlalchemy.future import select
from ..models.channel import Channel
from ..models.db_helper import db_helper

logger = logging.getLogger(__name__)


class ChannelRepository:
    def __init__(self):
        self.db = db_helper.session_getter

    async def select_all_channels(self):
        """Получение всех каналов из базы данных."""
        async with self.db() as session:
            result = await session.execute(select(Channel).order_by(Channel.id))
            channels = result.scalars().all()
            logger.info("Получены все каналы из базы данных.")
            return channels

    async def add_channel(self, channel):
        """Добавление нового канала в базу данных."""
        async with self.db() as session:
            try:
                new_channel = Channel(
                    id=await self.get_next_id(),
                    folder_id=channel["folder_id"],
                    channel_id=channel["channel_id"],
                    channel_name=channel["channel_name"],
                    channel_stats="test",
                    access_hash=channel["access_hash"],
                )
                session.add(new_channel)
                await session.commit()
                logger.info(f"Канал {channel['channel_name']} добавлен в базу данных.")
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Ошибка при добавлении канала {channel['channel_name']}: {e}"
                )
                return f"Ошибка. Проблема с запросом в базу данных _ add channel.\n{e}"
        return "True"

    async def get_next_id(self):
        """Получение следующего ID для канала."""
        async with self.db() as session:
            result = await session.execute(
                select(Channel).order_by(Channel.id.desc()).limit(1)
            )
            last_id = result.scalars().first()
            return last_id.id + 1 if last_id else 1

    async def select_channels_by_folder_id(self, folder_id):
        """Получение каналов по ID папки."""
        async with self.db() as session:
            result = await session.execute(
                select(Channel).filter(Channel.folder_id == folder_id)
            )
            channels = result.scalars().all()
            logger.info(f"Получены каналы для папки с ID {folder_id}.")
            return channels

    async def update_all_channels_id(self):
        """Обновление ID всех каналов."""
        channels = await self.select_all_channels()
        index = 1
        async with self.db() as session:
            for channel in channels:
                channel.id = index + 2000
                index += 1
            await session.commit()
            index = 1
            for channel in channels:
                channel.id = index
                index += 1
            await session.commit()
            logger.info("Обновлены ID всех каналов.")
        return "True"

    async def delete_channels_by_folder(self, folder_id):
        """Удаление каналов по ID папки."""
        async with self.db() as session:
            try:
                await session.execute(
                    select(Channel).filter(Channel.folder_id == folder_id).delete()
                )
                await session.commit()
                logger.info(f"Удалены каналы для папки с ID {folder_id}.")
            except Exception as e:
                await session.rollback()
                logger.error(
                    f"Ошибка при удалении каналов для папки с ID {folder_id}: {e}"
                )
                return "Ошибка, проблема с базой данных."
        await self.update_all_channels_id()
        return "True"

    async def delete_channel_by_id(self, channel_id):
        """Удаление канала по ID."""
        async with self.db() as session:
            try:
                await session.execute(
                    select(Channel).filter(Channel.channel_id == channel_id).delete()
                )
                await session.commit()
                logger.info(f"Удален канал с ID {channel_id}.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при удалении канала с ID {channel_id}: {e}")
                return "Ошибка, проблема с базой данных."
        await self.update_all_channels_id()
        return "True"

    async def change_channel_status(self, channel_id, status):
        """Изменение статуса канала."""
        async with self.db() as session:
            try:
                result = await session.execute(
                    select(Channel).filter(Channel.channel_id == channel_id)
                )
                channel = result.scalars().first()
                channel.channel_stats = status
                await session.commit()
                logger.info(f"Статус канала {channel_id} изменен на {status}.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при изменении статуса канала {channel_id}: {e}")
                return (
                    "Ошибка. Что то пошло не так.\nНе получилось изменить статус папки."
                )
        await self.update_all_channels_id()
        return "True"

    async def select_channels_by_id(self, channel_id):
        """Получение канала по ID."""
        async with self.db() as session:
            result = await session.execute(
                select(Channel).filter(Channel.channel_id == channel_id)
            )
            channel = result.scalars().first()
            logger.info(f"Получен канал с ID {channel_id}.")
            return channel

    async def select_channels_by_row_id(self, id):
        """Получение канала по ID строки."""
        async with self.db() as session:
            result = await session.execute(select(Channel).filter(Channel.id == id))
            channel = result.scalars().first()
            logger.info(f"Получен канал с ID строки {id}.")
            return channel
