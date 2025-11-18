import logging
from typing import List, Optional

from sqlalchemy import and_, select

from src.bot.dao.base import BaseDAO
from src.bot.enum.gender import Gender
from src.bot.models.user import Users
from src.core.database import async_session_maker

logger = logging.getLogger(__name__)


class UsersDAO(BaseDAO):
    model = Users  # type: ignore

    @classmethod
    async def update_user_data(cls, tg_id: int, **update_data):
        """
        Обновляет данные пользователя по tg_id
        """
        async with async_session_maker() as session:
            # Находим пользователя в этой же сессии

            result = await session.execute(select(cls.model).where(cls.model.tg_id == tg_id))  # type: ignore
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
    async def get_by_tg_id(cls, tg_id: int) -> Users:
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.tg_id == tg_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, user_id: int) -> Users:
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_next_profile(
        cls, user_id: int, rated_user_ids: List[int], gender_interest: Gender
    ) -> Optional[Users]:
        async with async_session_maker() as session:
            query = select(cls.model).where(
                and_(
                    cls.model.tg_id != user_id,
                    cls.model.name.isnot(None),
                    cls.model.age.isnot(None),
                    cls.model.city.isnot(None),
                )
            )

            if rated_user_ids:
                query = query.where(cls.model.tg_id.not_in(rated_user_ids))

            if gender_interest == Gender.MALE:
                query = query.where(cls.model.user_gender == Gender.MALE)
            elif gender_interest == Gender.FEMALE:
                query = query.where(cls.model.user_gender == Gender.FEMALE)
            # SKIP_GENDER → без фильтра

            query = query.order_by(cls.model.id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def get_profiles_by_ids(cls, not_rated_yet):
        async with async_session_maker() as session:
            users_query = select(Users).where(Users.tg_id.in_(not_rated_yet))
            users_result = await session.execute(users_query)
            return users_result.scalars().all()

    @classmethod
    async def set_status_questionnaire_true(cls, tg_id: int):
        return await cls.update_user_data(tg_id, status_of_the_questionnaire=True)

    @classmethod
    async def set_status_questionnaire_false(cls, tg_id: int):
        return await cls.update_user_data(tg_id, status_of_the_questionnaire=False)
