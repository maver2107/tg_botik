from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.dao.user import UsersDAO
from src.bot.states.form_states import FormStates

start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет, я Бот для закомств!")
    if message.from_user is None:
        await message.answer("❌ Пожалуйста, авторизуйся")
        return

    user = await UsersDAO.get_by_tg_id(message.from_user.id)
    if user is None:
        await UsersDAO.add(tg_id=message.from_user.id, username=message.from_user.username)
        await state.set_state(FormStates.waiting_for_name)
        await message.answer("Давай заполним твою анкету. Как тебя зовут?")
    else:
        await message.answer(
            "Ты уже зарегистрирован!\n\nКоманды:\n/search - начать просмотр анкет\n/matches - посмотреть мэтчи"
        )
