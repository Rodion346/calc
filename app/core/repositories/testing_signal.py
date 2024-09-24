import logging
from sqlalchemy.future import select

from ..models.db_helper import db_helper
from ..models.testsignal import TestingSignal

logger = logging.getLogger(__name__)

class TestingSignalRepository:
    def __init__(self):
        self.db = db_helper.session_getter

    async def select_all_testing_signals(self):
        """Получение всех тестовых сигналов из базы данных."""
        async with self.db() as session:
            result = await session.execute(select(TestingSignal).order_by(TestingSignal.id))
            signals = result.scalars().all()
            logger.info("Получены все тестовые сигналы из базы данных.")
            return signals

    async def add_new_testing_signal(self, signals):
        """Добавление новых тестовых сигналов в базу данных."""
        async with self.db() as session:
            for signal in signals:
                try:
                    new_signal = TestingSignal(
                        channel_id=signal[0]['channel_id'],
                        message_id=signal[0]['message_id'],
                        channel_name=signal[0]['channel_name'],
                        date=signal[0]['date'],
                        time=signal[0]['time'],
                        coin=signal[0]['coin'],
                        trend=signal[0]['trend'],
                        tvh=signal[0]['tvh'],
                        rvh=signal[0]['rvh'],
                        lvh=str(signal[0]['lvh']),
                        targets=str(signal[0]['targets']),
                        stop_less=signal[0]['stop_less'],
                        leverage=signal[0]['leverage'],
                        margin=signal[0]['margin']
                    )
                    session.add(new_signal)
                    logger.info(f"Тестовый сигнал {signal[0]['channel_name']} добавлен в базу данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при добавлении тестового сигнала {signal[0]['channel_name']}: {e}")
                    return 'Ошибка. Проблема с запросом в базу данных.'
            await session.commit()
        return 'True'

    async def change_testing_signal(self, signals):
        """Изменение тестовых сигналов в базе данных."""
        async with self.db() as session:
            for signal in signals:
                try:
                    existing_signal = await session.execute(select(TestingSignal).filter(
                        TestingSignal.channel_id == signal[0]['channel_id'],
                        TestingSignal.message_id == signal[0]['message_id']
                    ))
                    existing_signal = existing_signal.scalars().first()
                    if existing_signal:
                        existing_signal.channel_name = signal[0]['channel_name']
                        existing_signal.date = signal[0]['date']
                        existing_signal.time = signal[0]['time']
                        existing_signal.coin = signal[0]['coin']
                        existing_signal.trend = signal[0]['trend']
                        existing_signal.tvh = signal[0]['tvh']
                        existing_signal.rvh = signal[0]['rvh']
                        existing_signal.lvh = str(signal[0]['lvh'])
                        existing_signal.targets = str(signal[0]['targets'])
                        existing_signal.stop_less = signal[0]['stop_less']
                        existing_signal.leverage = signal[0]['leverage']
                        existing_signal.margin = signal[0]['margin']
                        logger.info(f"Тестовый сигнал {signal[0]['channel_name']} изменен в базе данных.")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Ошибка при изменении тестового сигнала {signal[0]['channel_name']}: {e}")
                    return 'Ошибка. Проблема с запросом в базу данных.'
            await session.commit()
        return 'True'
