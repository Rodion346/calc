import logging
from sqlalchemy.future import select

from ..models.db_helper import db_helper
from ..models.folder import Folder

logger = logging.getLogger(__name__)


class FolderRepository:
    def __init__(self):
        self.db = db_helper.session_getter

    async def select_all_folders(self):
        """Получение всех папок из базы данных."""
        async with self.db() as session:
            result = await session.execute(select(Folder))
            folders = result.scalars().all()
            logger.info("Получены все папки из базы данных.")
            return folders

    async def add_folders(self, folders):
        """Добавление новых папок в базу данных."""
        async with self.db() as session:
            for folder in folders:
                try:
                    new_folder = Folder(
                        folder_id=folder["id"],
                        folder_title=folder["title"],
                        folder_status="disable",
                    )
                    session.add(new_folder)
                    logger.info(f"Папка {folder['title']} добавлена в базу данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при добавлении папки {folder['title']}: {e}")
                    return f'Ошибка, проблема с базой данных. Папка {folder["title"]} не была добавлена. Ошибка: {e}'
            await session.commit()
        return "True"

    async def delete_folders(self, folders):
        """Удаление папок из базы данных."""
        async with self.db() as session:
            for folder in folders:
                try:
                    await session.execute(
                        select(Folder).filter(Folder.id == folder[0]).delete()
                    )
                    logger.info(f"Папка {folder['title']} удалена из базы данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при удалении папки {folder['title']}: {e}")
                    return f'Ошибка, проблема с базой данных. Папка {folder["title"]} Не была удалена.'
            await session.commit()
        return "True"

    async def select_folder_by_id(self, folder_id):
        """Получение папки по ID."""
        async with self.db() as session:
            result = await session.execute(
                select(Folder).filter(Folder.folder_id == folder_id)
            )
            folder = result.scalars().first()
            logger.info(f"Получена папка с ID {folder_id}.")
            return folder

    async def select_all_active_folders(self):
        """Получение всех активных папок."""
        async with self.db() as session:
            result = await session.execute(
                select(Folder).filter(Folder.folder_status == "active")
            )
            folders = result.scalars().all()
            logger.info("Получены все активные папки.")
            return folders

    async def change_folder_status(self, folder_id, status):
        """Изменение статуса папки."""
        async with self.db() as session:
            try:
                result = await session.execute(
                    select(Folder).filter(Folder.folder_id == folder_id)
                )
                folder = result.scalars().first()
                folder.folder_status = status
                await session.commit()
                logger.info(f"Статус папки {folder_id} изменен на {status}.")
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка при изменении статуса папки {folder_id}: {e}")
                return (
                    "Ошибка. Что то пошло не так.\nНе получилось изменить статус папки."
                )
        return "True"
