from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.states.form_states import FormStates
from src.users.dao import UsersDAO

start_router = Router()


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
