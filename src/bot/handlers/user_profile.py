from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.enum.user_profile import UserProfile
from src.bot.handlers.swipe import start_search
from src.bot.keyboards.user_profile import get_user_profile_keyboard
from src.bot.presenters.swipe import SwipePresenter
from src.bot.presenters.user_profile import UserProfilePresenter
from src.bot.services.swipe import SwipeService
from src.bot.services.user_profile import UserProfileService
from src.bot.states.form_states import UserProfileStates

user_router = Router()


@user_router.message(Command("my_profile"))
async def show_my_profile(
    message: Message,
    user_profile_service: UserProfileService,
    user_profile_presenter: UserProfilePresenter,
    state: FSMContext,
):
    user_id = message.from_user.id
    user = await user_profile_service.get_user_profile(user_id)
    await user_profile_presenter.send_user_profile(message, user)
    await message.answer("Хотите что то изменить?", reply_markup=get_user_profile_keyboard())
    await state.set_state(UserProfileStates.main_menu)


@user_router.message(F.text == UserProfile.get_button_text(UserProfile.SEARCH), UserProfileStates.main_menu)
async def swipe_start_search(
    message: Message, swipe_service: SwipeService, swipe_presenter: SwipePresenter, state: FSMContext
):
    await state.clear()
    await start_search(message, swipe_service, swipe_presenter, state)


@user_router.message(F.text == UserProfile.get_button_text(UserProfile.OFF_PROFILE), UserProfileStates.main_menu)
async def off_profile(message: Message, user_profile_service: UserProfileService, state: FSMContext):
    tg_id = message.from_user.id
    await user_profile_service.off_profile(tg_id)
    await message.answer(
        'Анкета отключена. Если захотите ее включить, то нажмите на "👀 Смотреть анкеты", либо напишите /search'
    )
