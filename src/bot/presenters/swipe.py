from aiogram.types import Message, ReplyKeyboardRemove

from src.bot.keyboards.swipe import get_swipe_keyboard
from src.bot.models.user import Users


class SwipePresenter:
    @staticmethod
    def format_profile(user: Users) -> str:
        """Отображение и форматирование текста анкеты"""
        profile_text = f"{user.name}, {user.age}, {user.city} - {user.interests}"

        return profile_text

    @staticmethod
    async def send_profile(message: Message, profile: Users):
        profile_text = SwipePresenter.format_profile(profile)
        keyboard = get_swipe_keyboard()
        if profile.photo_id:
            await message.answer_photo(photo=profile.photo_id, caption=profile_text, reply_markup=keyboard)
        else:
            await message.answer(profile_text, reply_markup=keyboard)

    @staticmethod
    def format_match_message(matched_user: Users) -> str:
        """Форматирование сообщения о мэтче"""
        username = f"@{matched_user.username}" if matched_user.username else "без username"
        return f"🔥 Взаимная симпатия!\n\nВы понравились друг другу!\nКонтакт: {username}\n\nМожете начать общение! 💬"

    @staticmethod
    def format_like_notification() -> str:
        """Сообщение 'Ты кому-то понравился'"""
        return "❤️ Ты кому-то понравился!\n\nПоказать кто это?"

    @staticmethod
    async def send_no_profiles_message(message: Message):
        """Сообщение когда анкеты закончились"""
        text = "😔 К сожалению, подходящих анкет пока нет. Попробуй позже!"

        await message.answer(text, reply_markup=ReplyKeyboardRemove())
