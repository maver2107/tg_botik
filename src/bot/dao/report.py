from sqlalchemy import delete, or_

from src.bot.dao.base import BaseDAO
from src.bot.models.report import Reports
from src.core.database import async_session_maker


class ReportsDAO(BaseDAO):
    model = Reports  # type: ignore

    @classmethod
    async def add_report(cls, reporter_user_id: int, target_user_id: int, comment: str):
        """Добавить жалобу"""
        await cls.add(reporter_user_id=reporter_user_id, target_user_id=target_user_id, comment=comment)

    @classmethod
    async def delete_reports_by_user(cls, tg_id: int):
        async with async_session_maker() as session:
            query = delete(cls.model).where(
                or_(
                    cls.model.reporter_user_id == tg_id,
                    cls.model.target_user_id == tg_id,
                )
            )
            await session.execute(query)
            await session.commit()
