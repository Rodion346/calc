from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TestingSignal(Base):
    __tablename__ = 'testing_signals'

    channel_id: Mapped[str] = mapped_column(nullable=False)
    message_id: Mapped[str] = mapped_column(nullable=False)
    channel_name: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    time: Mapped[str] = mapped_column(nullable=False)
    coin: Mapped[str] = mapped_column(nullable=False)
    trend: Mapped[str] = mapped_column(nullable=False)
    tvh: Mapped[str] = mapped_column(nullable=False)
    rvh: Mapped[str] = mapped_column(nullable=False)
    lvh: Mapped[str] = mapped_column(nullable=False)
    targets: Mapped[str] = mapped_column(nullable=False)
    stop_less: Mapped[str] = mapped_column(nullable=False)
    leverage: Mapped[str] = mapped_column(nullable=False)
    margin: Mapped[str] = mapped_column(nullable=False)