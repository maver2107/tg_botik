from aiogram.types import Message

from src.bot.models.user import Users
from src.bot.presenters.swipe import SwipePresenter


class UserProfilePresenter(SwipePresenter):
    @staticmethod
    async def send_user_profile(message: Message, profile: Users):
        """Отправка анкеты пользователю"""
        profile_text = SwipePresenter.format_profile(profile)
        await message.answer_photo(photo=profile.photo_id, caption=profile_text)
