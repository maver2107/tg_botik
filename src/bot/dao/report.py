from src.bot.dao.base import BaseDAO
from src.bot.models.report import Reports


class ReportsDAO(BaseDAO):
    model = Reports  # type: ignore

    @classmethod
    async def add_report(cls, reporter_user_id: int, target_user_id: int, comment: str):
        """Добавить жалобу"""
        await cls.add(reporter_user_id=reporter_user_id, target_user_id=target_user_id, comment=comment)
