from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states.form_states import FormStates
from src.users.dao import UsersDAO

start_router = Router()

#TODO !
"""
Роутер не должен в себе хранить бизнес логику
Вся логика взаимодействий с бд - отдельно в DAO, а бизнес логика должнa быть в модуле services (это так называемая черная коробка)
Тут максимум принимаем запросы (Роутер/хендлер) - отправляем в services (бизнес логика) - отправляем в DAO (взаимодействие с БД)
В папке /bot/services/start.py - это путь для модуля где должна быть бизнес логика
Спроси у ИИ что это означает

Надо добавлять loger для дебага и логирования (спроси у ии что это)
"""

@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет, я Бот для закомств!")

    user_exists = await UsersDAO.exists(tg_id=message.from_user.id)

    if not user_exists:
        await UsersDAO.add(tg_id=message.from_user.id)

        await state.set_state(FormStates.waiting_for_name)
        await message.answer("Давай заполним твою анкету. Как тебя зовут?")
    else:
        await message.answer("Ты уже зарегестрирован")
