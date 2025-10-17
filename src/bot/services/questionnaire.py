# src/bot/services/questionnaire.py
import logging

from aiogram.fsm.context import FSMContext

from src.bot.models.gender import Gender
from src.bot.models.responses import AgeResponse, GenderResponse
from src.bot.states.form_states import FormStates
from src.users.dao import UsersDAO

logger = logging.getLogger(__name__)


class QuestionnaireService:
    def __init__(self, users_dao: UsersDAO):
        self.users_dao = users_dao

    async def process_name(self, name: str, state: FSMContext) -> str:
        """Обработка имени"""
        logger.info(f"Обработка имени: {name}")
        cleaned_name = name.strip()
        await state.update_data(name=cleaned_name)
        await state.set_state(FormStates.waiting_for_age)
        return f"Приятно познакомиться, {cleaned_name}! Сколько тебе лет?"

    async def process_age(self, age_text: str, state: FSMContext) -> AgeResponse:
        """Обработка возраста"""
        logger.info(f"Обработка возраста: {age_text}")
        try:
            age = int(age_text.strip())
            if age < 10 or age > 100:
                logger.warning(f"Некорректный возраст: {age}")
                return AgeResponse(success=False, message="Пожалуйста, введите реальный возраст (10-100):")

            await state.update_data(age=age)
            await state.set_state(FormStates.waiting_for_gender)
            logger.debug(f"Возраст {age} принят")
            return AgeResponse(success=True, message="age_processed")

        except ValueError:
            logger.warning(f"Нечисловой возраст: {age_text}")
            return AgeResponse(success=False, message="Пожалуйста, введите число:")

    async def process_gender(self, gender_text: str, state: FSMContext) -> GenderResponse:
        """Обработка пола"""
        logger.info(f"Обработка пола: {gender_text}")

        if gender_text == Gender.get_display_name(Gender.MALE):
            gender = Gender.MALE
        elif gender_text == Gender.get_display_name(Gender.FEMALE):
            gender = Gender.FEMALE
        else:
            logger.warning(f"Неизвестный пол: {gender_text}")
            return GenderResponse(success=False, message="Пожалуйста, выбери пол из предложенных вариантов:")

        await state.update_data(user_gender=gender)
        await state.set_state(FormStates.waiting_for_gender_interest)
        logger.debug(f"Пол {gender} принят")
        return GenderResponse(success=True, message="gender_processed")

    async def process_gender_interest(self, gender_interest_text: str, state: FSMContext) -> GenderResponse:
        """Обработка предпочтений по полу"""
        logger.info(f"Обработка gender_interest: {gender_interest_text}")

        if gender_interest_text == Gender.get_display_gender_interest(Gender.MALE):
            gender_interest = Gender.MALE
        elif gender_interest_text == Gender.get_display_gender_interest(Gender.FEMALE):
            gender_interest = Gender.FEMALE
        elif gender_interest_text == Gender.get_display_gender_interest(Gender.SKIP_GENDER):
            gender_interest = Gender.SKIP_GENDER
        else:
            logger.warning(f"Неизвестный gender_interest: {gender_interest_text}")
            return GenderResponse(success=False, message="Пожалуйста, выбери из предложенных вариантов:")

        await state.update_data(gender_interest=gender_interest)
        await state.set_state(FormStates.waiting_for_city)
        logger.debug(f"Gender interest {gender_interest} принят")
        return GenderResponse(success=True, message="gender_interest_processed")

    async def process_city(self, city: str, state: FSMContext) -> str:
        """Обработка города"""
        logger.info(f"Обработка города: {city}")
        cleaned_city = city.strip()
        await state.update_data(city=cleaned_city)
        await state.set_state(FormStates.waiting_for_interests)
        logger.debug(f"Город {cleaned_city} принят")
        return "Расскажи о своих интересах (хобби, увлечения):"

    async def process_interests(self, interests: str, state: FSMContext) -> str:
        """Обработка интересов"""
        logger.info("Обработка интересов")
        await state.update_data(interests=interests.strip())
        await state.set_state(FormStates.waiting_for_photo)
        logger.debug("Интересы приняты, переход к фото")
        return (
            "📸 Отправь своё фото для профиля\n\n"
            "Это поможет другим пользователям узнать тебя лучше!\n"
            "Можешь пропустить этот шаг, нажав кнопку ниже."
        )

    async def complete_questionnaire(self, photo_id: str, user_id: int, state: FSMContext) -> str:
        """Завершение опроса и сохранение данных"""
        logger.info(f"Завершение опроса для пользователя {user_id}")

        form_data = await state.get_data()

        # Сохраняем в базу
        await self.users_dao.update_user_data(
            tg_id=user_id,
            name=form_data.get("name"),
            age=form_data.get("age"),
            user_gender=form_data.get("user_gender"),
            gender_interest=form_data.get("gender_interest"),
            city=form_data.get("city"),
            interests=form_data.get("interests"),
            photo_id=photo_id,
        )

        await state.clear()
        logger.info(f"Опрос завершен для пользователя {user_id}")

        caption = (
            f"{form_data.get('name')}, {form_data.get('age')}, {form_data.get('city')} – {form_data.get('interests')}"
        )
        return caption, photo_id
