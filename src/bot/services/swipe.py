# src/bot/services/swipe.py
"""
TODO для джуна: Очистка Service от UI-логики

ПРОБЛЕМЫ В ЭТОМ ФАЙЛЕ:
1. Service импортирует клавиатуры (строка 10) - это UI, не бизнес-логика
2. Service отправляет Telegram-сообщения (строки 136-151) - это должен делать Handler/Presenter
3. format_profile() - это UI-функция, должна быть в Presenter
4. Service создаёт БД-сессии напрямую (строки 33, 80) - должно быть в DAO

ПЛАН РЕФАКТОРИНГА:
1. Убрать импорт get_show_likes_keyboard - клавиатуры должен создавать Presenter
2. Убрать bot.send_message из process_like - вместо этого вернуть данные:
   return {
       "is_match": bool,
       "matched_user": Users | None,
       "notification_needed": bool,  # нужно ли отправить уведомление
       "next_profile": Users | None
   }
3. Переместить format_profile в SwipePresenter
4. Вынести get_next_profile и get_profiles_who_liked_me в DAO
5. Service должен только координировать DAO и возвращать структурированные данные

ПРАВИЛЬНАЯ СТРУКТУРА Service:
- Принимает данные от Handler
- Вызывает методы DAO для работы с БД
- Применяет бизнес-правила (проверка взаимных лайков, создание мэтчей)
- Возвращает данные Handler'у для отображения
"""

import logging
from typing import Optional

from sqlalchemy import and_, select

from src.bot.dao.like import LikesDAO, MatchesDAO
from src.bot.dao.user import UsersDAO
from src.bot.models.user import Users
from src.core.database import async_session_maker

logger = logging.getLogger(__name__)


class SwipeService:
    def __init__(self, likes_dao: LikesDAO, matches_dao: MatchesDAO, users_dao: UsersDAO):
        self.likes_dao = likes_dao
        self.matches_dao = matches_dao
        self.users_dao = users_dao

    async def get_next_profile(cls, user_id: int) -> Optional[Users]:
        # 1. Получаем текущего пользователя
        current_user = await cls.users_dao.get_by_tg_id(user_id)
        if not current_user:
            logger.error(f"Пользователь {user_id} не найден")
            return None

        # 2. Получаем ID всех уже оценённых пользователей
        rated_user_ids = await cls.likes_dao.get_rated_user_ids(user_id)

        # 3. Получаем следующую анкету
        next_profile = await cls.users_dao.get_next_profile(
            user_id=user_id,
            rated_user_ids=rated_user_ids,
            gender_interest=current_user.gender_interest,
        )

        return next_profile

    async def get_profiles_who_liked_me(self, user_id: int) -> list[Users]:
        """
        Получить анкеты пользователей, которые лайкнули текущего пользователя,
        но он их ещё не оценил
        """
        # TODO: ПРОБЛЕМА - Работа с БД в Service
        # Перенести в DAO: likes_dao.get_profiles_who_liked_me(user_id)
        async with async_session_maker() as session:
            # Получаем ID пользователей, которые лайкнули текущего
            liked_me_query = select(self.likes_dao.model.from_user_id).where(
                and_(self.likes_dao.model.to_user_id == user_id, self.likes_dao.model.is_like.is_(True))
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
        # TODO: КРИТИЧЕСКАЯ ПРОБЛЕМА - Service отправляет сообщения!
        # bot не должен быть параметром Service!
        #
        # ПРАВИЛЬНЫЙ ПОДХОД:
        # 1. Service обрабатывает лайк и возвращает данные
        # 2. Handler получает эти данные и решает что отправить
        # 3. Presenter форматирует и отправляет сообщения
        #
        # Нужно:
        # - Удалить параметр bot
        # - Удалить bot.send_message (строки 136-151)
        # - ИСПОЛЬЗОВАТЬ PYDANTIC МОДЕЛИ вместо dict!
        #
        # Создай модель в src/bot/models/responses.py:
        # class LikeProcessResult(BaseModel):
        #     is_match: bool
        #     matched_user: Users | None
        #     current_user: Users
        #     next_profile: Users | None
        #
        # И возвращай:
        # return LikeProcessResult(
        #     is_match=is_match,
        #     matched_user=matched_user,
        #     current_user=current_user,
        #     next_profile=next_profile
        # )
        #
        # ПРЕИМУЩЕСТВА Pydantic:
        # - Автодополнение в IDE (result.is_match вместо result["is_match"])
        # - Валидация типов
        # - Защита от опечаток в ключах
        # - Документирование структуры данных

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

            # TODO: УДАЛИТЬ ЭТО! Отправка сообщений не должна быть в Service
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
            # TODO: УДАЛИТЬ ЭТО! Отправка сообщений не должна быть в Service
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
        # TODO: ИСПОЛЬЗОВАТЬ PYDANTIC МОДЕЛИ вместо dict!
        #
        # Создай модель в src/bot/models/responses.py:
        # class DislikeProcessResult(BaseModel):
        #     next_profile: Users | None
        #
        # И возвращай: return DislikeProcessResult(next_profile=next_profile)

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
        # TODO: УДАЛИТЬ ЭТОТ МЕТОД!
        # Форматирование - это UI-логика, должна быть в Presenter
        # Создай SwipePresenter и перенеси туда:
        # class SwipePresenter:
        #     @staticmethod
        #     def format_profile(user: Users, hide_name: bool = False) -> str:
        #         ...

        profile_text = f"{user.name}, {user.age}, {user.city} - {user.interests}"

        return profile_text
