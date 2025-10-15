import asyncio

from src.application import start_bot
from src.logger import setup_logging

if __name__ == "__main__":
    setup_logging()
    asyncio.run(start_bot())
