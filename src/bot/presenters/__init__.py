from src.bot.presenters.swipe import SwipePresenter


def get_swipe_presenter() -> SwipePresenter:
    """Фабрика для создания сервиса свайпов"""
    return SwipePresenter()
