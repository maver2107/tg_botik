# src/bot/keyboards/swipe.py
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.bot.enum.like import ApplicationStatus, LikeStatus
from src.bot.enum.user_profile import UserProfile


def get_swipe_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопками лайк/дизлайк"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=LikeStatus.get_display_name(LikeStatus.LIKE)),
                KeyboardButton(text=LikeStatus.get_display_name(LikeStatus.DISLIKE)),
            ]
        ],
        resize_keyboard=True,
    )


def get_show_likes_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для предложения показать тех, кто лайкнул"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=ApplicationStatus.show_application(ApplicationStatus.SHOW)),
                KeyboardButton(text=ApplicationStatus.show_application(ApplicationStatus.SKIP)),
            ]
        ],
        resize_keyboard=True,
    )


def get_search_only_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора пола с использованием ENUM"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=UserProfile.get_button_text(UserProfile.SEARCH))]],
        resize_keyboard=True,
    )
