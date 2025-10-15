from src.bot.services.questionnaire import QuestionnaireService
from src.users.dao import UsersDAO


def get_questionnaire_service() -> QuestionnaireService:
    """Фабрика для создания сервиса опросника"""
    return QuestionnaireService(users_dao=UsersDAO)
