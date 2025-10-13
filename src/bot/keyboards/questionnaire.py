# src/bot/keyboards/questionnaire.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from src.bot.models.gender import Gender


def get_gender_keyboard() -> ReplyKeyboardMarkup:
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


def remove_keyboard() -> ReplyKeyboardRemove:
    """Удаление клавиатуры"""
    return ReplyKeyboardRemove()
