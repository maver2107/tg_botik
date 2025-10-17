# src/likes/models.py
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Likes(Base):
    """Модель лайков между пользователями"""

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    to_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    is_like: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True = like, False = dislike
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Matches(Base):
    """Модель мэтчей (взаимных лайков)"""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    user2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.tg_id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
