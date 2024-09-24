from sqlalchemy.orm import Mapped

from .base import Base


class User(Base):
    __tablename__ = "users"
    name: Mapped[str]
