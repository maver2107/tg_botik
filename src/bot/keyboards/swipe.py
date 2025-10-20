# src/bot/keyboards/swipe.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_swipe_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с кнопками лайк/дизлайк"""
    buttons = [
        [
            InlineKeyboardButton(text="❤️", callback_data=f"like_{user_id}"),
            InlineKeyboardButton(text="👎", callback_data=f"dislike_{user_id}"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


"""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
def get_swipe_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❤️", callback_data=f"like_{user_id}"),
                KeyboardButton(text="👎", callback_data=f"dislike_{user_id}"),
            ]
        ],
        resize_keyboard=True,
    )
"""


def get_show_likes_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для предложения показать тех, кто лайкнул"""
    buttons = [
        [
            InlineKeyboardButton(text="❌ Нет, спасибо", callback_data="show_likes_no"),
            InlineKeyboardButton(text="✅ Да, показать!", callback_data="show_likes_yes"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
