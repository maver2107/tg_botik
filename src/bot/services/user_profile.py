import logging

from src.bot.dao.like import LikesDAO, MatchesDAO
from src.bot.dao.user import UsersDAO
from src.bot.models.user import Users

logger = logging.getLogger(__name__)


class UserProfileService:
    def __init__(self, likes_dao: LikesDAO, matches_dao: MatchesDAO, users_dao: UsersDAO):
        self.likes_dao = likes_dao
        self.matches_dao = matches_dao
        self.users_dao = users_dao

    async def get_user_profile(self, user_id: int) -> Users:
        # 1. Получаем текущего пользователя
        current_user = await self.users_dao.get_by_tg_id(user_id)
        if not current_user:
            logger.error(f"Пользователь {user_id} не найден")
            return None

        return current_user
