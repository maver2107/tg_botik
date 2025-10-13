import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers.questionnaire import questionnaire_router
from src.bot.handlers.start import start_router
from src.bot.services import get_questionnaire_service  # Импортируем фабрику
from src.config import settings


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # 🔧 НАСТРОЙКА ЗАВИСИМОСТЕЙ
    # Регистрируем сервисы в workflow_data
    dp.workflow_data["questionnaire_service"] = get_questionnaire_service()

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(questionnaire_router)

    # Запуск бота
    await dp.start_polling(bot)


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)


if __name__ == "__main__":
    asyncio.run(main())
