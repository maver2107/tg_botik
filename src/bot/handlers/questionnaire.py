from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.states.form_states import FormStates
from src.users.dao import UsersDAO

questionnaire_router = Router()


@questionnaire_router.message(FormStates.waiting_for_name)
async def cmd_start(message: Message, state: FSMContext):
    name = message.text.strip()

    await state.update_data(name=name)

    await state.set_state(FormStates.waiting_for_age)
    await message.answer(f"Приятно познакомиться, {name}! Сколько тебе лет?")


@questionnaire_router.message(FormStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        if age < 10 or age > 100:
            await message.answer("Пожалуйста, введите реальный возраст (10-100):")
            return

        await state.update_data(age=age)
        await state.set_state(FormStates.waiting_for_gender)

        gender_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="👨 Мужской"), KeyboardButton(text="👩 Женский")]], resize_keyboard=True
        )
        await message.answer("Выбери свой пол:", reply_markup=gender_keyboard)

    except ValueError:
        await message.answer("Пожалуйста, введите число:")


@questionnaire_router.message(FormStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender_text = message.text.strip()

    # Преобразуем текст в значение для базы
    gender_map = {"👨 Мужской": "male", "👩 Женский": "female"}

    if gender_text not in gender_map:
        await message.answer("Пожалуйста, выбери пол из предложенных вариантов:")
        return

    gender = gender_map[gender_text]
    await state.update_data(user_gender=gender)
    await state.set_state(FormStates.waiting_for_city)

    await message.answer("Из какого ты города?", reply_markup=ReplyKeyboardRemove())


@questionnaire_router.message(FormStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(city=city)
    await state.set_state(FormStates.waiting_for_interests)
    await message.answer("Расскажи о своих интересах (хобби, увлечения):")


@questionnaire_router.message(FormStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext):
    interests = message.text.strip()

    # Получаем все данные из состояния
    form_data = await state.get_data()

    # Сохраняем в базу данных
    await UsersDAO.update_user_data(
        tg_id=message.from_user.id,
        name=form_data.get("name"),
        age=form_data.get("age"),
        user_gender=form_data.get("user_gender"),
        city=form_data.get("city"),
        interests=interests,
    )

    # Завершаем состояние
    await state.clear()

    await message.answer(
        f"🎉 Анкета заполнена! Вот твои данные:\n"
        f"{form_data.get('name')}, {form_data.get('age')}, {form_data.get('city')} - {interests}"
    )
