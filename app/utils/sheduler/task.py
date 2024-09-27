import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.util import await_only

from core.models.db_helper import db_helper
from core.repositories import ChannelRepository
from core.repositories import FolderRepository
from telegram.telethon_client import TelegramClientWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
channelRepo = ChannelRepository(db_helper.session_getter)
folderRepo = FolderRepository(db_helper.session_getter)


async def check_and_add_channel(folders_name):
    await client_wrapper.start()
    folders = await client_wrapper.get_folders()
    for folder in folders:
        if folder.title in folders_name:
            channels = await channelRepo.select_channels_by_folder_id(folder.title)
            for entity in folder.include_peers:
                entity_info = await client_wrapper.client.get_entity(entity)
                if hasattr(entity_info, "megagroup") or hasattr(
                    entity_info, "broadcast"
                ):
                    if entity_info not in channels:
                        await channelRepo.add_channel(entity_info, folder.title)
    await folderRepo.add_folders(folders)
    await client_wrapper.stop()


if __name__ == "__main__":
    folders_l = ["RF", "DF"]
    client_wrapper = TelegramClientWrapper()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_add_channel, "interval", seconds=10, args=[folders_l])
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
