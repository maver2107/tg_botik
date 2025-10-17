from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_profile_rating_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оценки анкеты"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❤️ Лайк", callback_data="like"),
                InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip"),
            ]
        ]
    )


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню после регистрации"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👀 Смотреть анкеты", callback_data="view_profiles"),
                InlineKeyboardButton(text="💕 Мои мэтчи", callback_data="view_matches"),
            ],
            [
                InlineKeyboardButton(text="📝 Редактировать анкету", callback_data="edit_profile"),
            ],
        ]
    )
