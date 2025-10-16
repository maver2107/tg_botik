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


def get_gender_interest_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=Gender.get_display_gender_interest(Gender.MALE)),
                KeyboardButton(text=Gender.get_display_gender_interest(Gender.FEMALE)),
                KeyboardButton(text=Gender.get_display_gender_interest(Gender.SKIP_GENDER)),
            ]
        ],
        resize_keyboard=True,
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Удаление клавиатуры"""
    return ReplyKeyboardRemove()
