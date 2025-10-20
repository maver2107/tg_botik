# src/bot/services/swipe.py
import logging
from typing import Optional

from sqlalchemy import and_, select

from src.bot.dao.like import LikesDAO, MatchesDAO
from src.bot.dao.user import UsersDAO
from src.bot.enum.gender import Gender
from src.bot.keyboards.swipe import get_show_likes_keyboard
from src.bot.models.user import Users
from src.core.database import async_session_maker

logger = logging.getLogger(__name__)


class SwipeService:
    def __init__(self, likes_dao: LikesDAO, matches_dao: MatchesDAO, users_dao: UsersDAO):
        self.likes_dao = likes_dao
        self.matches_dao = matches_dao
        self.users_dao = users_dao

    async def get_next_profile(self, user_id: int) -> Optional[Users]:
        """
        Получить следующую анкету для просмотра

        Логика:
        - Исключаем самого пользователя
        - Исключаем уже оценённых пользователей
        - Фильтруем по gender_interest
        - Возвращаем случайную анкету
        """
        async with async_session_maker() as session:
            # Получаем данные текущего пользователя
            current_user_query = select(Users).where(Users.tg_id == user_id)
            current_user_result = await session.execute(current_user_query)
            current_user = current_user_result.scalar_one_or_none()

            if not current_user:
                logger.error(f"Пользователь {user_id} не найден")
                return None

            # Получаем ID всех уже оценённых пользователей
            rated_users_query = select(self.likes_dao.model.to_user_id).where(
                self.likes_dao.model.from_user_id == user_id
            )
            rated_users_result = await session.execute(rated_users_query)
            rated_user_ids = [row[0] for row in rated_users_result.all()]

            # Формируем запрос для поиска подходящих анкет
            query = select(Users).where(
                and_(
                    Users.tg_id != user_id,  # Не показываем себя
                    Users.tg_id.not_in(rated_user_ids) if rated_user_ids else True,  # Исключаем оценённых
                    Users.name.isnot(None),  # Только заполненные анкеты
                    Users.age.isnot(None),
                    Users.city.isnot(None),
                )
            )

            # Фильтрация по gender_interest
            if current_user.gender_interest == Gender.MALE:
                query = query.where(Users.user_gender == Gender.MALE)
            elif current_user.gender_interest == Gender.FEMALE:
                query = query.where(Users.user_gender == Gender.FEMALE)
            # Если SKIP_GENDER - показываем всех

            # Получаем случайную анкету
            query = query.order_by(Users.id)
            result = await session.execute(query)
            next_profile = result.scalars().first()

            return next_profile

    async def get_profiles_who_liked_me(self, user_id: int) -> list[Users]:
        """
        Получить анкеты пользователей, которые лайкнули текущего пользователя,
        но он их ещё не оценил
        """
        async with async_session_maker() as session:
            # Получаем ID пользователей, которые лайкнули текущего
            liked_me_query = select(self.likes_dao.model.from_user_id).where(
                and_(self.likes_dao.model.to_user_id == user_id, self.likes_dao.model.is_like == True)
            )
            liked_me_result = await session.execute(liked_me_query)
            liked_me_ids = [row[0] for row in liked_me_result.all()]

            if not liked_me_ids:
                return []

            # Получаем ID пользователей, которых текущий уже оценил
            rated_query = select(self.likes_dao.model.to_user_id).where(self.likes_dao.model.from_user_id == user_id)
            rated_result = await session.execute(rated_query)
            rated_ids = [row[0] for row in rated_result.all()]

            # Находим тех, кто лайкнул, но кого ещё не оценили
            not_rated_yet = [uid for uid in liked_me_ids if uid not in rated_ids]

            if not not_rated_yet:
                return []

            # Получаем анкеты этих пользователей
            users_query = select(Users).where(Users.tg_id.in_(not_rated_yet))
            users_result = await session.execute(users_query)
            return users_result.scalars().all()

    async def process_like(self, from_user_id: int, to_user_id: int, bot) -> dict:
        """
        Обработка лайка

        Возвращает:
        - is_match: bool - произошёл ли мэтч
        - next_profile: Users - следующая анкета
        - matched_user: Users - пользователь с которым мэтч (если есть)
        """
        logger.info(f"Лайк от {from_user_id} к {to_user_id}")

        # Добавляем лайк
        await self.likes_dao.add_like(from_user_id=from_user_id, to_user_id=to_user_id, is_like=True)

        # Проверяем взаимный лайк
        is_match = await self.likes_dao.check_mutual_like(from_user_id, to_user_id)

        matched_user = None
        if is_match:
            # Создаём мэтч
            await self.matches_dao.create_match(from_user_id, to_user_id)
            logger.info(f"🔥 MATCH! {from_user_id} и {to_user_id}")

            # Получаем данные обоих пользователей для обмена username
            matched_user = await self.users_dao.get_by_tg_id(to_user_id)
            current_user = await self.users_dao.get_by_tg_id(from_user_id)

            # Отправляем уведомление второму пользователю о мэтче
            try:
                await bot.send_message(
                    to_user_id,
                    f"🔥 Взаимная симпатия!\n\n"
                    f"Вы понравились друг другу с @{current_user.username if hasattr(current_user, 'username') else 'пользователем'}!\n"
                    f"Можете начать общение! 💬",
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление о мэтче пользователю {to_user_id}: {e}")
        else:
            # Если НЕ мэтч - отправляем уведомление "Ты кому-то понравился"
            try:
                await bot.send_message(
                    to_user_id, "❤️ Ты кому-то понравился!\n\nПоказать кто это?", reply_markup=get_show_likes_keyboard()
                )
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {to_user_id}: {e}")

        # Получаем следующую анкету
        next_profile = await self.get_next_profile(from_user_id)

        return {"is_match": is_match, "next_profile": next_profile, "matched_user": matched_user}

    async def process_dislike(self, from_user_id: int, to_user_id: int) -> dict:
        """
        Обработка дизлайка
        """
        logger.info(f"Дизлайк от {from_user_id} к {to_user_id}")

        # Добавляем дизлайк
        await self.likes_dao.add_like(from_user_id=from_user_id, to_user_id=to_user_id, is_like=False)

        # Получаем следующую анкету
        next_profile = await self.get_next_profile(from_user_id)

        return {"next_profile": next_profile}

    def format_profile(self, user: Users) -> str:
        """
        Форматирование анкеты для отображения

        hide_name - скрыть имя (для показа тех, кто лайкнул)
        """

        profile_text = f"{user.name}, {user.age}, {user.city} - {user.interests}"

        return profile_text
