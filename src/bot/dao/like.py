# src/likes/dao.py
from typing import List
from sqlalchemy import and_, or_, select

from src.bot.dao.base import BaseDAO
from src.bot.models.like import Likes, Matches
from src.core.database import async_session_maker


class LikesDAO(BaseDAO):
    model = Likes  # type: ignore

    @classmethod
    async def add_like(cls, from_user_id: int, to_user_id: int, is_like: bool):
        """Добавить лайк или дизлайк"""
        await cls.add(from_user_id=from_user_id, to_user_id=to_user_id, is_like=is_like)

    @classmethod
    async def check_mutual_like(cls, user1_id: int, user2_id: int) -> bool:
        """Проверка взаимного лайка"""
        async with async_session_maker() as session:
            # Проверяем, что оба пользователя лайкнули друг друга
            query = select(cls.model).where(  # type: ignore
                or_(
                    and_(
                        cls.model.from_user_id == user1_id,  # type: ignore
                        cls.model.to_user_id == user2_id,  # type: ignore
                        cls.model.is_like == True,  # type: ignore
                    ),
                    and_(
                        cls.model.from_user_id == user2_id,  # type: ignore
                        cls.model.to_user_id == user1_id,  # type: ignore
                        cls.model.is_like == True,  # type: ignore
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

    @classmethod
    async def get_rated_user_ids(cls, from_user_id: int) -> List[int]:
        async with async_session_maker() as session:
            query = select(cls.model.to_user_id).where(cls.model.from_user_id == from_user_id)
            result = await session.execute(query)
            return [row[0] for row in result.all()]


class MatchesDAO(BaseDAO):
    model = Matches  # type: ignore

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
            query = select(cls.model).where(  # type: ignore
                or_(
                    cls.model.user1_id == user_id,  # type: ignore
                    cls.model.user2_id == user_id,  # type: ignore
                )
            )
            result = await session.execute(query)
            return result.scalars().all()
