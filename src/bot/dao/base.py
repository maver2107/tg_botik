from sqlalchemy import delete, insert, select  # TODO: добавить update

from src.core.database import async_session_maker


class BaseDAO:
    model = None

    # TODO: Вот примерная реализация метода update_by_id в базовом классе
    # @classmethod
    # async def update_by_id(cls, model_id: int, **update_data):
    #     async with async_session_maker() as session:
    #         # Находим объект
    #         query = select(cls.model).where(cls.model.id == model_id)
    #         result = await session.execute(query)
    #         instance = result.scalar_one_or_none()

    #         if not instance:
    #             return None

    #         # Обновляем атрибуты на ЭКЗЕМПЛЯРЕ
    #         for key, value in update_data.items():
    #             if value is not None and hasattr(instance, key):
    #                 setattr(instance, key, value)

    #         await session.commit()
    #         await session.refresh(instance)
    #         return instance

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add(cls, **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_by_id(cls, id):
        async with async_session_maker() as session:
            query = delete(cls.model).where(cls.model.id == id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def exists(cls, **filter_by) -> bool:
        """Проверяет существование записи по фильтрам"""
        record = await cls.find_one_or_none(**filter_by)
        return record is not None
