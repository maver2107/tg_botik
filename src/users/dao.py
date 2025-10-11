from sqlalchemy import select

from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.users.models import Users


class UsersDAO(BaseDAO):
    model = Users

    @classmethod
    async def update_user_data(cls, tg_id: int, **update_data):
        """
        Обновляет данные пользователя по tg_id
        """
        async with async_session_maker() as session:
            # Находим пользователя в этой же сессии

            result = await session.execute(select(cls.model).where(cls.model.tg_id == tg_id))
            user = result.scalar_one_or_none()

            if not user:
                print(f"❌ Пользователь с tg_id {tg_id} не найден")
                return None

            # Обновляем поля
            for key, value in update_data.items():
                if value is not None and hasattr(user, key):
                    setattr(user, key, value)

            # Коммитим изменения
            await session.commit()

            # Обновляем объект из БД
            await session.refresh(user)

            print(f"✅ Данные пользователя {tg_id} обновлены")
            return user

    @classmethod
    async def get_by_tg_id(cls, tg_id: int):
        """Получить пользователя по tg_id"""
        return await cls.find_one_or_none(tg_id=tg_id)
