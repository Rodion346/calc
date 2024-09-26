from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqladmin import Admin, ModelView

from core.models import Channel, Folder
from core.models.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)
admin = Admin(main_app, db_helper.engine)


class Channels(ModelView, model=Channel):
    column_list = [
        Channel.id,
        Channel.channel_id,
        Channel.channel_name,
        Channel.channel_stats,
        Channel.folder_id,
    ]


class Folders(ModelView, model=Folder):
    column_list = [
        Folder.id,
        Folder.folder_id,
        Folder.folder_title,
        Folder.folder_status,
    ]


admin.add_view(Channels)
admin.add_view(Folders)
