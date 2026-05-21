from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.models.user import Users
from src.bot.presenters.swipe import SwipePresenter


class UserProfilePresenter(SwipePresenter):
    @staticmethod
    async def send_user_profile(message: Message, profile: Users):
        profile_text = SwipePresenter.format_profile(profile)
        await message.answer("Вот ваша анкета!", reply_markup=ReplyKeyboardRemove())
        if profile.photo_id:
            await message.answer_photo(photo=profile.photo_id, caption=profile_text)
        else:
            await message.answer(profile_text)
