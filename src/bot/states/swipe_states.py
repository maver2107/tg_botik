# src/bot/states/swipe_states.py
from aiogram.fsm.state import State, StatesGroup


class SwipeStates(StatesGroup):
    """Состояния для свайп-системы"""

    normal_browsing = State()  # Обычный просмотр анкет
    viewing_likes = State()  # Просмотр тех, кто лайкнул
