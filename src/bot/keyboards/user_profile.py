# src/bot/keyboards/questionnaire.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.enum.gender import Gender


def get_user_profile_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора пола с использованием ENUM"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=Gender.get_display_name(Gender.MALE)),
                KeyboardButton(text=Gender.get_display_name(Gender.FEMALE)),
            ]
        ],
        resize_keyboard=True,
    )
