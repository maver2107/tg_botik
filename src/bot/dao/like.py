# src/likes/dao.py

from typing import List, Sequence

from sqlalchemy import and_, delete, or_, select

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
                        cls.model.is_like.is_(True),  # type: ignore
                    ),
                    and_(
                        cls.model.from_user_id == user2_id,  # type: ignore
                        cls.model.to_user_id == user1_id,  # type: ignore
                        cls.model.is_like.is_(True),  # type: ignore
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
        """ID всех анкет, которые пользователь уже оценил (лайк или дизлайк)"""
        async with async_session_maker() as session:
            query = select(cls.model.to_user_id).where(
                cls.model.from_user_id == from_user_id  # type: ignore
            )
            result = await session.execute(query)
            return [row[0] for row in result.all()]

    @classmethod
    async def get_users_who_liked_me(cls, user_id: int) -> List[int]:
        """ID пользователей, которые лайкнули меня"""
        async with async_session_maker() as session:
            liked_me_query = select(cls.model.from_user_id).where(
                and_(
                    cls.model.to_user_id == user_id,  # type: ignore
                    cls.model.is_like.is_(True),  # type: ignore
                )
            )
            liked_me_result = await session.execute(liked_me_query)
            liked_me_ids = [row[0] for row in liked_me_result.all()]
            return liked_me_ids

    @classmethod
    async def get_users_i_liked_from_list(
        cls,
        user_id: int,
        other_user_ids: Sequence[int],
    ) -> list[int]:
        """
        НОВЫЙ МЕТОД.
        Вернуть из списка other_user_ids только тех, кого user_id лайкнул (is_like = True).
        Дизлайки не учитываются.
        """
        if not other_user_ids:
            return []

        async with async_session_maker() as session:
            query = select(cls.model.to_user_id).where(  # type: ignore
                cls.model.from_user_id == user_id,  # type: ignore
                cls.model.to_user_id.in_(other_user_ids),  # type: ignore
                cls.model.is_like.is_(True),  # type: ignore
            )
            result = await session.execute(query)
            return [row[0] for row in result.all()]

    @classmethod
    async def get_users_i_disliked_from_list(
        cls,
        user_id: int,
        other_user_ids: Sequence[int],
    ) -> list[int]:
        """
        Вернуть из списка other_user_ids тех, кому user_id поставил дизлайк (is_like = False).
        """
        if not other_user_ids:
            return []

        async with async_session_maker() as session:
            query = select(cls.model.to_user_id).where(  # type: ignore
                cls.model.from_user_id == user_id,  # type: ignore
                cls.model.to_user_id.in_(other_user_ids),  # type: ignore
                cls.model.is_like.is_(False),  # type: ignore
            )
            result = await session.execute(query)
            return [row[0] for row in result.all()]

    @classmethod
    async def delete_likes_by_user(cls, tg_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).where(
                or_(
                    cls.model.from_user_id == tg_id,  # type: ignore
                    cls.model.to_user_id == tg_id,  # type: ignore
                )
            )
            await session.execute(query)
            await session.commit()


class MatchesDAO(BaseDAO):
    model = Matches  # type: ignore

    @classmethod
    async def create_match(cls, user1_id: int, user2_id: int):
        """Создать мэтч"""
        # Сортируем ID, чтобы избежать дубликатов (1-2 и 2-1)
        if user1_id > user2_id:
            user1_id, user2_id = user2_id, user1_id
        await cls.add(user1_id=user1_id, user2_id=user2_id)

    # TODO: Думаю можно переделать метод find_all в базовом классе и передавать параметры фильтрации в параметрах
    # Вот примерная реализация метода find_all в базовом классе
    # @classmethod
    # async def find_all(cls, *where_args, **filter_by):
    #     """
    #     Универсальный поиск.
    #     :param where_args: Аргументы для сложных условий (or_, >, <, и т.д.)
    #     :param filter_by: Аргументы для точного совпадения (id=1, name='test')
    #     """
    #     async with async_session_maker() as session:
    #         query = select(cls.model)

    #         if filter_by:
    #             query = query.filter_by(**filter_by)

    #         if where_args:
    #             query = query.where(*where_args)

    #         result = await session.execute(query)
    #         return result.scalars().all()
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

    @classmethod
    async def delete_matches_by_user(cls, tg_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).where(
                or_(
                    cls.model.user1_id == tg_id,  # type: ignore
                    cls.model.user2_id == tg_id,  # type: ignore
                )
            )
            await session.execute(query)
            await session.commit()
