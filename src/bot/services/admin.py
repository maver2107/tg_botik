import logging

from aiogram import Bot

from src.bot.dao.report import ReportsDAO
from src.bot.dao.user import UsersDAO
from src.bot.models.report import Reports
from src.bot.models.user import Users

logger = logging.getLogger(__name__)

USERS_PER_PAGE = 5
REPORTS_PER_PAGE = 5


class AdminService:
    def __init__(self, users_dao: type[UsersDAO], reports_dao: type[ReportsDAO]):
        self.users_dao = users_dao
        self.reports_dao = reports_dao

    async def get_users_page(self, page: int) -> tuple[list[Users], int, int]:
        offset = (page - 1) * USERS_PER_PAGE
        users = await self.users_dao.get_paginated(limit=USERS_PER_PAGE, offset=offset)
        total = await self.users_dao.count()
        total_pages = max(1, (total + USERS_PER_PAGE - 1) // USERS_PER_PAGE)
        return users, page, total_pages

    async def get_user_detail(self, tg_id: int) -> Users | None:
        return await self.users_dao.get_by_tg_id(tg_id)

    async def ban_user(self, tg_id: int, report_id: int | None = None) -> None:
        await self.users_dao.update_user_data(tg_id, is_banned=True)
        if report_id is not None:
            from datetime import datetime, timezone

            await self.reports_dao.update(report_id, reviewed_at=datetime.now(timezone.utc))

    async def unban_user(self, tg_id: int) -> None:
        await self.users_dao.update_user_data(tg_id, is_banned=False)

    async def get_reports_page(self, page: int, reviewed: bool) -> tuple[list[Reports], int, int]:
        offset = (page - 1) * REPORTS_PER_PAGE
        reports = await self.reports_dao.get_paginated_by_reviewed(
            reviewed=reviewed, limit=REPORTS_PER_PAGE, offset=offset
        )
        total = await self.reports_dao.count_by_reviewed(reviewed=reviewed)
        total_pages = max(1, (total + REPORTS_PER_PAGE - 1) // REPORTS_PER_PAGE)
        return reports, page, total_pages

    async def get_report_detail(self, report_id: int) -> tuple[Reports, Users | None, Users | None] | None:
        report = await self.reports_dao.find_one_or_none(id=report_id)
        if not report:
            return None
        reporter = await self.users_dao.get_by_tg_id(report.reporter_user_id)
        target = await self.users_dao.get_by_tg_id(report.target_user_id)
        return report, reporter, target

    async def dismiss_report(self, report_id: int) -> None:
        from datetime import datetime, timezone

        await self.reports_dao.update(report_id, reviewed_at=datetime.now(timezone.utc))

    async def broadcast(self, bot: Bot, text: str) -> tuple[int, int]:
        import asyncio

        sent = 0
        failed = 0
        offset = 0
        while True:
            users = await self.users_dao.get_paginated(limit=50, offset=offset)
            if not users:
                break
            for u in users:
                try:
                    await bot.send_message(chat_id=u.tg_id, text=text)
                    sent += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.05)  # ~20 msg/s, safe under Telegram 30/s limit
            offset += 50
        return sent, failed
