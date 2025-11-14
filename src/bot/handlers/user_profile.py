from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.bot.presenters.user_profile import UserProfilePresenter
from src.bot.services.user_profile import UserProfileService

user_router = Router()


@user_router.message(Command("my_profile"))
async def show_my_profile(
    message: Message, user_profile_service: UserProfileService, user_profile_presenter: UserProfilePresenter
):
    user_id = message.from_user.id
    user = await user_profile_service.get_user_profile(user_id)
    await user_profile_presenter.send_user_profile(message, user)
