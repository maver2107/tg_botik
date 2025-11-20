from src.bot.presenters.swipe import SwipePresenter
from src.bot.presenters.user_profile import UserProfilePresenter


def get_swipe_presenter() -> SwipePresenter:
    """Фабрика для создания сервиса свайпов"""
    return SwipePresenter()


def get_user_profile_presenter() -> UserProfilePresenter:
    return UserProfilePresenter()
