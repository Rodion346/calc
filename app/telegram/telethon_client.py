from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogFiltersRequest
from telethon.tl.types import InputPeerEmpty, DialogFilter
from app.core.repositories.folder import FolderRepository
from app.core.repositories.channel import ChannelRepository
from app.core.models.db_helper import db_helper


channelRepo = ChannelRepository(db_helper.session_getter)


class TelegramClientWrapper:
    def __init__(
        self,
        api_id=26515046,
        api_hash="22b6dbdfce28e71ce66911f29ccc5bfe",
        session_name="session",
    ):
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.previous_channels = {}

    async def start(self):
        await self.client.start()

    async def stop(self):
        await self.client.disconnect()

    async def get_folders(self):
        result = await self.client(GetDialogFiltersRequest())
        folders = []
        for folder in result.filters:
            if isinstance(folder, DialogFilter):
                folders.append(folder)
        return folders

    async def get_channel_in_folders(self, folder_names):
        folders = await self.get_folders()
        channels = []
        for folder in folders:
            if folder.title in folder_names:
                for entity in folder.include_peers:
                    entity_info = await self.client.get_entity(entity)
                    if hasattr(entity_info, "megagroup") or hasattr(
                        entity_info, "broadcast"
                    ):
                        channels.append(entity_info)
        return channels


if __name__ == "__main__":
    import asyncio

    client_wrapper = TelegramClientWrapper()

    async def main():
        await client_wrapper.start()
        folders = ["RF", "DF"]
        ch = await client_wrapper.get_folders()
        for i in ch:
            print(i)
        await client_wrapper.stop()

    asyncio.run(main())
