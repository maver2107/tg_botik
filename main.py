import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.handlers.questionnaire import questionnaire_router
from src.bot.handlers.start import start_router
from src.config import settings


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(start_router)
    dp.include_router(questionnaire_router)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
