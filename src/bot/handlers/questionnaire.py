# src/bot/handlers/questionnaire.py
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.keyboards.questionnaire import get_gender_keyboard, remove_keyboard
from src.bot.services.questionnaire import QuestionnaireService
from src.bot.states.form_states import FormStates

questionnaire_router = Router()


@questionnaire_router.message(FormStates.waiting_for_name)
async def process_name(
    message: Message,
    state: FSMContext,
    questionnaire_service: QuestionnaireService,  # Автоматически внедрится
):
    """Только прием запроса и возврат ответа"""
    response = await questionnaire_service.process_name(message.text, state)
    await message.answer(response)


@questionnaire_router.message(FormStates.waiting_for_age)
async def process_age(
    message: Message,
    state: FSMContext,
    questionnaire_service: QuestionnaireService,  # Автоматически внедрится
):
    """Только прием запроса и возврат ответа"""
    result = await questionnaire_service.process_age(message.text, state)

    if result["success"]:
        await message.answer("Выбери свой пол:", reply_markup=get_gender_keyboard())
    else:
        await message.answer(result["message"])


# Аналогично для остальных хендлеров...
@questionnaire_router.message(FormStates.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    result = await questionnaire_service.process_gender(message.text, state)

    if result["success"]:
        await message.answer("Из какого ты города?", reply_markup=remove_keyboard())
    else:
        await message.answer(result["message"])


@questionnaire_router.message(FormStates.waiting_for_city)
async def process_city(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    response = await questionnaire_service.process_city(message.text, state)
    await message.answer(response)


@questionnaire_router.message(FormStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext, questionnaire_service: QuestionnaireService):
    response = await questionnaire_service.complete_questionnaire(message.text, message.from_user.id, state)
    await message.answer(response)
