# src/bot/keyboards/questionnaire.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.bot.enum.user_profile import UserProfile


def get_user_profile_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора пола с использованием ENUM"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=UserProfile.get_button_text(UserProfile.SEARCH)),
                KeyboardButton(text=UserProfile.get_button_text(UserProfile.EDIT_PROFILE)),
                KeyboardButton(text=UserProfile.get_button_text(UserProfile.OFF_PROFILE)),
            ]
        ],
        resize_keyboard=True,
    )
