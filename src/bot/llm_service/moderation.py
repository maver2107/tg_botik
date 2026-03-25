from langchain_core.runnables import Runnable

from src.bot.llm_service.prompt_templates.schemas import ProfileCheck
from src.logger import logger


class ModerationService:
    def __init__(self, chain: Runnable):
        self.chain = chain

    async def moderate_profile(self, profile_text: str) -> ProfileCheck:
        try:
            result = await self.chain.ainvoke({"profile_text": profile_text})
            return result
        except Exception as e:
            logger.error(f"Error moderating profile: {e}")
            return None

    async def valid_text(self, profile_text: str) -> ProfileCheck:
        result = await self.moderate_profile(profile_text)
        print(result)
        if result.is_valid:
            return True
        return False
