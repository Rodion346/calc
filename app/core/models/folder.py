from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Folder(Base):
    __tablename__ = "folders"

    folder_id: Mapped[str] = mapped_column(unique=True, nullable=False)
    folder_title: Mapped[str] = mapped_column(nullable=False)
    folder_status: Mapped[str] = mapped_column(nullable=False)
