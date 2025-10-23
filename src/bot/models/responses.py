# src/bot/models/responses.py
from datetime import datetime

from pydantic import BaseModel

from bot.models.user import Users


class BaseResponse(BaseModel):
    """Базовая модель ответа"""

    success: bool
    message: str


class AgeResponse(BaseResponse):
    """Ответ для обработки возраста"""

    pass


class GenderResponse(BaseResponse):
    """Ответ для обработки пола"""

    pass


class LikeProcessResult(BaseModel):
    """Результат обработки лайка"""

    model_config = {"arbitrary_types_allowed": True}

    is_match: bool
    matched_user: Users | None
    current_user: Users
    next_profile: Users | None


class DislikeProcessResult(BaseModel):
    """Результат обработки дизлайка"""

    model_config = {"arbitrary_types_allowed": True}

    next_profile: Users | None


class MatchWithDetails(BaseModel):
    """Мэтч с подробной информацией"""

    model_config = {"arbitrary_types_allowed": True}

    user: Users
    match_date: datetime | None = None
