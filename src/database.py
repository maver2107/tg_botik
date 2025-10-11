from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(url=DATABASE_URL)
# Создаем фабрику сессий для взаимодействия с базой данных
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# Базовый класс для всех моделей
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него
