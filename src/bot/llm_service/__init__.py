from src.bot.llm_service.client import llm, prompt
from src.bot.llm_service.moderation import ModerationService
from src.bot.llm_service.prompt_templates.schemas import ProfileCheck


def get_moderation_service() -> ModerationService:
    """Фабрика для создания сервиса модерации"""
    chain = prompt | llm.with_structured_output(ProfileCheck)
    return ModerationService(chain=chain)
