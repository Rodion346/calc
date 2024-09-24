from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Channel(Base):
    __tablename__ = "channels"

    folder_id: Mapped[str] = mapped_column(nullable=False)
    channel_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(nullable=False)
    channel_stats: Mapped[str] = mapped_column(nullable=False)
    access_hash: Mapped[str] = mapped_column(nullable=False)
