# test_tg_bot_specific.py
import asyncio
import asyncpg
from src.config import settings


async def test_tg_bot_specific():
    try:
        print("Testing specific connection to tg_bot database...")
        print(f"Connection details: {settings.DB_USER}@localhost:5432/tg_bot")

        conn = await asyncpg.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            database=settings.DB_NAME,  # tg_bot
            timeout=10,
        )

        print("✅ Connection to tg_bot successful!")

        # Проверим, что можем выполнять запросы
        result = await conn.fetchval("SELECT 1")
        print(f"Test query result: {result}")

        # Проверим существующие таблицы
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)

        print("Tables in tg_bot:")
        for table in tables:
            print(f"  - {table['table_name']}")

        await conn.close()
        return True

    except Exception as e:
        print(f"❌ Connection to tg_bot failed: {e}")
        return False


asyncio.run(test_tg_bot_specific())
