# src/likes/dao.py
from sqlalchemy import and_, or_, select

from src.dao.base import BaseDAO
from src.database import async_session_maker
from src.likes.models import Likes, Matches


class LikesDAO(BaseDAO):
    model = Likes

    @classmethod
    async def add_like(cls, from_user_id: int, to_user_id: int, is_like: bool):
        """Добавить лайк или дизлайк"""
        await cls.add(from_user_id=from_user_id, to_user_id=to_user_id, is_like=is_like)

    @classmethod
    async def check_mutual_like(cls, user1_id: int, user2_id: int) -> bool:
        """Проверка взаимного лайка"""
        async with async_session_maker() as session:
            # Проверяем, что оба пользователя лайкнули друг друга
            query = select(cls.model).where(
                or_(
                    and_(
                        cls.model.from_user_id == user1_id, cls.model.to_user_id == user2_id, cls.model.is_like == True
                    ),
                    and_(
                        cls.model.from_user_id == user2_id, cls.model.to_user_id == user1_id, cls.model.is_like == True
                    ),
                )
            )
            result = await session.execute(query)
            likes = result.scalars().all()

            # Если есть 2 лайка (взаимные), это мэтч
            return len(likes) == 2

    @classmethod
    async def get_user_likes(cls, user_id: int):
        """Получить все лайки пользователя"""
        return await cls.find_all(from_user_id=user_id, is_like=True)

    @classmethod
    async def already_rated(cls, from_user_id: int, to_user_id: int) -> bool:
        """Проверка, оценивал ли пользователь уже эту анкету"""
        like = await cls.find_one_or_none(from_user_id=from_user_id, to_user_id=to_user_id)
        return like is not None


class MatchesDAO(BaseDAO):
    model = Matches

    @classmethod
    async def create_match(cls, user1_id: int, user2_id: int):
        """Создать мэтч"""
        # Сортируем ID чтобы избежать дубликатов (1-2 и 2-1)
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id

        await cls.add(user1_id=user1_id, user2_id=user2_id)

    @classmethod
    async def get_user_matches(cls, user_id: int):
        """Получить все мэтчи пользователя"""
        async with async_session_maker() as session:
            query = select(cls.model).where(or_(cls.model.user1_id == user_id, cls.model.user2_id == user_id))
            result = await session.execute(query)
            return result.scalars().all()
