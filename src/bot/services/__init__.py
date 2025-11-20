# src/bot/services/__init__.py
from src.bot.dao.like import LikesDAO, MatchesDAO
from src.bot.dao.user import UsersDAO
from src.bot.services.questionnaire import QuestionnaireProcessService
from src.bot.services.swipe import SwipeService
from src.bot.services.user_profile import UserProfileService


def get_questionnaire_service() -> QuestionnaireProcessService:
    """Фабрика для создания сервиса опросника"""
    return QuestionnaireProcessService(users_dao=UsersDAO)


def get_swipe_service() -> SwipeService:
    """Фабрика для создания сервиса свайпов"""
    return SwipeService(likes_dao=LikesDAO, matches_dao=MatchesDAO, users_dao=UsersDAO)


def get_user_profile_service() -> UserProfileService:
    """Фабрика для создания сервиса свайпов"""
    return UserProfileService(likes_dao=LikesDAO, matches_dao=MatchesDAO, users_dao=UsersDAO)
