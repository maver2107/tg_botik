from sqlalchemy import func, select

from src.bot.dao.base import BaseDAO
from src.bot.models.report import Reports
from src.core.database import async_session_maker


class ReportsDAO(BaseDAO):
    model = Reports  # type: ignore

    @classmethod
    async def add_report(cls, reporter_user_id: int, target_user_id: int, comment: str):
        await cls.add(reporter_user_id=reporter_user_id, target_user_id=target_user_id, comment=comment)

    @classmethod
    async def report_exists(cls, reporter_user_id: int, target_user_id: int) -> bool:
        return await cls.exists(reporter_user_id=reporter_user_id, target_user_id=target_user_id)

    @classmethod
    async def get_paginated_by_reviewed(cls, reviewed: bool, limit: int, offset: int):
        async with async_session_maker() as session:
            where = Reports.reviewed_at.isnot(None) if reviewed else Reports.reviewed_at.is_(None)
            order = Reports.id.desc() if reviewed else Reports.id
            query = select(Reports).where(where).order_by(order).limit(limit).offset(offset)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def count_by_reviewed(cls, reviewed: bool) -> int:
        async with async_session_maker() as session:
            where = Reports.reviewed_at.isnot(None) if reviewed else Reports.reviewed_at.is_(None)
            query = select(func.count()).select_from(Reports).where(where)
            result = await session.execute(query)
            return result.scalar() or 0
