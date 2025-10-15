# src/bot/services/questionnaire.py
import logging

from aiogram.fsm.context import FSMContext

from src.bot.models.gender import Gender
from src.bot.models.responses import AgeResponse, GenderResponse  # Импортируем Pydantic модели
from src.bot.states.form_states import FormStates
from src.users.dao import UsersDAO

logger = logging.getLogger(__name__)


class QuestionnaireService:
    def __init__(self, users_dao: UsersDAO):
        self.users_dao = users_dao

    async def process_name(self, name: str, state: FSMContext) -> str:
        """Обработка имени - бизнес-логика"""
        logger.info(f"Обработка имени: {name=}")
        cleaned_name = name.strip()
        await state.update_data(name=cleaned_name)
        await state.set_state(FormStates.waiting_for_age)
        return f"Приятно познакомиться, {cleaned_name}! Сколько тебе лет?"

    async def process_age(self, age_text: str, state: FSMContext) -> AgeResponse:
        """Обработка возраста - бизнес-логика"""
        logger.info(f"Обработка возраста: {age_text=}")
        try:
            age = int(age_text.strip())
            if age < 10 or age > 100:
                logger.warning(f"Некорректный возраст: {age=}")
                return AgeResponse(success=False, message="Пожалуйста, введите реальный возраст (10-100):")

            await state.update_data(age=age)
            await state.set_state(FormStates.waiting_for_gender)
            logger.debug(f"Возраст принят: {age=}")
            return AgeResponse(success=True, message="age_processed")

        except ValueError:
            logger.warning(f"Нечисловой возраст: {age_text=}")
            return AgeResponse(success=False, message="Пожалуйста, введите число:")

    async def process_gender(self, gender_text: str, state: FSMContext) -> GenderResponse:
        """Обработка пола - бизнес-логика с использованием ENUM"""
        logger.info(f"Обработка пола: {gender_text=}")

        # Используем ENUM вместо gender_map
        if gender_text == "👨 Мужской":
            gender = Gender.MALE
        elif gender_text == "👩 Женский":
            gender = Gender.FEMALE
        else:
            logger.warning(f"Неизвестный пол: {gender_text=}")
            return GenderResponse(success=False, message="Пожалуйста, выбери пол из предложенных вариантов:")

        await state.update_data(user_gender=gender)
        await state.set_state(FormStates.waiting_for_city)
        logger.debug(f"Пол принят: {gender=}")
        return GenderResponse(success=True, message="gender_processed")

    async def process_city(self, city: str, state: FSMContext) -> str:
        """Обработка города - бизнес-логика"""
        logger.info(f"Обработка города: {city=}")
        cleaned_city = city.strip()
        await state.update_data(city=cleaned_city)
        await state.set_state(FormStates.waiting_for_interests)
        logger.debug(f"Город принят: {cleaned_city=}")
        return "Расскажи о своих интересах (хобби, увлечения):"

    async def complete_questionnaire(self, interests: str, user_id: int, state: FSMContext) -> str:
        """Завершение опроса - бизнес-логика"""
        logger.info(f"Завершение опроса для пользователя: {user_id=}")

        form_data = await state.get_data()

        # Сохраняем в базу
        await self.users_dao.update_user_data(
            tg_id=user_id,
            name=form_data.get("name"),
            age=form_data.get("age"),
            user_gender=form_data.get("user_gender"),
            city=form_data.get("city"),
            interests=interests.strip(),
        )

        await state.clear()
        logger.info(f"Опрос завершен для пользователя: {user_id=}")

        # Красивое отображение пола в финальном сообщении
        gender_display = "👨 Мужской" if form_data.get("user_gender") == Gender.MALE else "👩 Женский"

        return (
            f"🎉 Анкета заполнена! Вот твои данные:\n"
            f"Имя: {form_data.get('name')}\n"
            f"Возраст: {form_data.get('age')}\n"
            f"Пол: {gender_display}\n"
            f"Город: {form_data.get('city')}\n"
            f"Интересы: {interests}"
        )
