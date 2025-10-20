from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers.questionnaire import questionnaire_router
from src.bot.handlers.start import start_router
from src.bot.handlers.swipe import swipe_router
from src.bot.services import get_questionnaire_service, get_swipe_service
from src.config import settings


def setup_bot() -> Bot:
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot


def setup_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    dp.workflow_data["questionnaire_service"] = get_questionnaire_service()
    dp.workflow_data["swipe_service"] = get_swipe_service()

    dp.include_router(start_router)
    dp.include_router(questionnaire_router)
    dp.include_router(swipe_router)
    return dp


async def start_bot():
    bot = setup_bot()
    dp = setup_dispatcher()

    await dp.start_polling(bot)
