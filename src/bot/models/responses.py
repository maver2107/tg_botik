# src/bot/models/responses.py
from pydantic import BaseModel
from typing import Optional


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
