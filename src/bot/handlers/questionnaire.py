# src/bot/handlers/questionnaire.py
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.keyboards.questionnaire import (
    get_gender_interest_keyboard,
    get_gender_keyboard,
    remove_keyboard,
)
from src.bot.services.questionnaire import QuestionnaireService
from src.bot.states.form_states import FormStates

questionnaire_router = Router()


@questionnaire_router.message(FormStates.waiting_for_name)
async def process_name(
    message: Message,
    state: FSMContext,
    questionnaire_service: QuestionnaireService,
):
    """Обработка имени"""
    response = await questionnaire_service.process_name(name=message.text, state=state)
    await message.answer(response)


@questionnaire_router.message(FormStates.waiting_for_age)
async def process_age(
    message: Message,
    state: FSMContext,
    questionnaire_service: QuestionnaireService,
):
    """Обработка возраста"""
    result = await questionnaire_service.process_age(age_text=message.text, state=state)

    if result.success:
        await message.answer("Выбери свой пол:", reply_markup=get_gender_keyboard())
    else:
        await message.answer(result.message)


@questionnaire_router.message(FormStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    """Обработка пола"""
    result = await questionnaire_service.process_gender(gender_text=message.text, state=state)

    if result.success:
        await message.answer("Кто тебе интересен?", reply_markup=get_gender_interest_keyboard())
    else:
        await message.answer(result.message)


@questionnaire_router.message(FormStates.waiting_for_gender_interest)
async def process_gender_interest(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    """Обработка предпочтений по полу"""
    result = await questionnaire_service.process_gender_interest(gender_interest_text=message.text, state=state)

    if result.success:
        await message.answer("Из какого ты города?", reply_markup=remove_keyboard())
    else:
        await message.answer(result.message)


@questionnaire_router.message(FormStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    """Обработка города"""
    response = await questionnaire_service.process_city(city=message.text, state=state)
    await message.answer(response)


@questionnaire_router.message(FormStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    """Обработка интересов"""
    response = await questionnaire_service.process_interests(interests=message.text, state=state)
    await message.answer(response)


# Обработчик фото
@questionnaire_router.message(FormStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    """Обработка фото профиля"""
    # Берём фото самого высокого качества (последнее в списке)
    photo_id = message.photo[-1].file_id

    caption, photo = await questionnaire_service.complete_questionnaire(
        photo_id=photo_id, user_id=message.from_user.id, state=state
    )

    if photo:
        await message.answer_photo(photo, caption=caption)


# Если пользователь отправил не фото
@questionnaire_router.message(FormStates.waiting_for_photo)
async def wrong_photo_format(message: Message):
    """Неверный формат - ожидалось фото"""
    await message.answer("❌ Пожалуйста, отправь фото'\n\nФото должно быть отправлено как изображение, а не файл.")
