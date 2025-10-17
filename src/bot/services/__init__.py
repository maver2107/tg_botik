from src.bot.services.questionnaire import QuestionnaireProcessService
from src.users.dao import UsersDAO


def get_questionnaire_service() -> QuestionnaireProcessService:
    """Фабрика для создания сервиса опросника"""
    return QuestionnaireProcessService(users_dao=UsersDAO)
