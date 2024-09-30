import logging
from sqlalchemy.future import select

from ..models.db_helper import db_helper
from ..models.signal import Signal

logger = logging.getLogger(__name__)

class SignalRepository:
    def __init__(self, db):
        self.db = db

    async def select_all_signals(self):
        """Получение всех сигналов из базы данных."""
        async with self.db() as session:
            result = await session.execute(select(Signal).order_by(Signal.id))
            signals = result.scalars().all()
            logger.info("Получены все сигналы из базы данных.")
            return signals

    async def add_new_signal(self, signals):
        """Добавление новых сигналов в базу данных."""
        async with self.db() as session:
            for signal in signals:
                try:
                    new_signal = Signal(
                        channel_id=signal['channel_id'],
                        message_id=signal['message_id'],
                        channel_name=signal['channel_name'],
                        date=signal['date'],
                        time=signal['time'],
                        coin=signal['Coin'],
                        trend=signal['trend'],
                        tvh=signal['tvh'],
                        rvh=signal['rvh'],
                        lvh=str(signal['lvh']),
                        targets=str(signal['targets']),
                        stop_less=signal['stop_less'],
                        leverage=signal['leverage'],
                        margin=signal['margin']
                    )
                    session.add(new_signal)
                    logger.info(f"Сигнал {signal['channel_name']} добавлен в базу данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при добавлении сигнала {signal['channel_name']}: {e}")
                    return 'Ошибка. Проблема с запросом в базу данных.'
            await session.commit()
        return 'True'

    async def change_signal(self, signals):
        """Изменение сигналов в базе данных."""
        async with self.db() as session:
            for signal in signals:
                try:
                    existing_signal = await session.execute(select(Signal).filter(
                        Signal.channel_id == signal['channel_id'],
                        Signal.message_id == signal['message_id']
                    ))
                    existing_signal = existing_signal.scalars().first()
                    if existing_signal:
                        existing_signal.channel_name = signal['channel_name']
                        existing_signal.date = signal['date']
                        existing_signal.time = signal['time']
                        existing_signal.coin = signal['coin']
                        existing_signal.trend = signal['trend']
                        existing_signal.tvh = signal['tvh']
                        existing_signal.rvh = signal['rvh']
                        existing_signal.lvh = str(signal['lvh'])
                        existing_signal.targets = str(signal['targets'])
                        existing_signal.stop_less = signal['stop_less']
                        existing_signal.leverage = signal['leverage']
                        existing_signal.margin = signal['margin']
                        logger.info(f"Сигнал {signal['channel_name']} изменен в базе данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при изменении сигнала {signal['channel_name']}: {e}")
                    return 'Ошибка. Проблема с запросом в базу данных.'
            await session.commit()
        return 'True'

    async def select_signals_by_date(self, date, time=None):
        """Получение сигналов по дате."""
        async with self.db() as session:
            if time:
                signals = await session.execute(select(Signal).filter(
                    (Signal.date > date) | ((Signal.date == date) & (Signal.time >= time))
                ))
            else:
                signals = await session.execute(select(Signal).filter(Signal.date >= date))
            signals = signals.scalars().all()
            logger.info(f"Получены сигналы по дате {date} и времени {time}.")
            return signals

    async def select_signals(self, pfilter=None):
        """Получение сигналов с фильтром."""
        async with self.db() as session:
            if pfilter:
                signals = await session.execute(select(Signal).filter(pfilter))
            else:
                signals = await session.execute(select(Signal))
            signals = signals.scalars().all()
            logger.info("Получены сигналы с фильтром.")
            return signals