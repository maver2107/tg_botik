import asyncio

from tg_bot.bot import run_bot
from tg_bot.db import create_db_pool, init_db


async def main():
    pool = await create_db_pool()
    await init_db(pool)
    await run_bot()


if __name__ == "__main__":
    asyncio.run(main())
