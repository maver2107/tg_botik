# src/bot/services/swipe.py


import logging

from src.bot.dao.like import LikesDAO, MatchesDAO
from src.bot.dao.user import UsersDAO
from src.bot.models.responses import DislikeProcessResult, LikeProcessResult, MatchWithDetails
from src.bot.models.user import Users

logger = logging.getLogger(__name__)


class SwipeService:
    def __init__(self, likes_dao: LikesDAO, matches_dao: MatchesDAO, users_dao: UsersDAO):
        self.likes_dao = likes_dao
        self.matches_dao = matches_dao
        self.users_dao = users_dao

    async def get_next_profile(self, user_id: int) -> Users:
        # 1. Получаем текущего пользователя
        current_user = await self.users_dao.get_by_tg_id(user_id)
        if not current_user:
            logger.error(f"Пользователь {user_id} не найден")
            return None

        # 2. Получаем ID всех уже оценённых пользователей
        rated_user_ids = await self.likes_dao.get_rated_user_ids(user_id)

        # 3. Получаем следующую анкету
        next_profile = await self.users_dao.get_next_profile(
            user_id=user_id,
            rated_user_ids=rated_user_ids,
            gender_interest=current_user.gender_interest,
        )

        return next_profile

    async def get_profiles_who_liked_me(self, user_id: int) -> list[Users]:
        """Получить анкеты тех, кто лайкнул меня"""
        # 1. Кто лайкнул
        liked_me_ids = await self.likes_dao.get_users_who_liked_me(user_id)
        if not liked_me_ids:
            return []

        # 2. Кого я ещё не оценил
        not_rated = await self.likes_dao.get_unrated_from_list(user_id, liked_me_ids)
        if not not_rated:
            return []

        # 3. Получить профили
        return await self.users_dao.get_profiles_by_ids(not_rated)

    async def process_like(self, from_user_id: int, to_user_id: int) -> LikeProcessResult:
        logger.info(f"Лайк от {from_user_id} к {to_user_id}")

        # Добавляем лайк
        await self.likes_dao.add_like(from_user_id=from_user_id, to_user_id=to_user_id, is_like=True)

        # Проверяем взаимный лайк
        is_match = await self.likes_dao.check_mutual_like(from_user_id, to_user_id)

        matched_user = None
        current_user = await self.users_dao.get_by_tg_id(from_user_id)
        if is_match:
            # Создаём мэтч
            await self.matches_dao.create_match(from_user_id, to_user_id)
            logger.info(f"🔥 MATCH! {from_user_id} и {to_user_id}")

            matched_user = await self.users_dao.get_by_tg_id(to_user_id)

        # Получаем следующую анкету
        next_profile = await self.get_next_profile(from_user_id)

        return LikeProcessResult(
            is_match=is_match, matched_user=matched_user, current_user=current_user, next_profile=next_profile
        )

    async def process_dislike(self, from_user_id: int, to_user_id: int) -> DislikeProcessResult:
        """
        Обработка дизлайка
        """

        logger.info(f"Дизлайк от {from_user_id} к {to_user_id}")

        # Добавляем дизлайк
        await self.likes_dao.add_like(from_user_id=from_user_id, to_user_id=to_user_id, is_like=False)

        # Получаем следующую анкету
        next_profile = await self.get_next_profile(from_user_id)

        return DislikeProcessResult(next_profile=next_profile)

    async def get_user_matches_with_details(self, user_id: int) -> list[MatchWithDetails]:
        """Получить мэтчи с данными пользователей"""
        matches = await self.matches_dao.get_user_matches(user_id)
        result = []

        for match in matches:
            other_id = match.user2_id if match.user1_id == user_id else match.user1_id
            other_user = await self.users_dao.get_by_tg_id(other_id)
            if other_user:
                result.append(MatchWithDetails(user=other_user, match_date=match.created_at))

        return result
