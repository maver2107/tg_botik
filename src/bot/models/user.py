from sqlalchemy import BigInteger, Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    age: Mapped[int] = mapped_column(nullable=True)
    user_gender: Mapped[str] = mapped_column(nullable=True)
    gender_interest: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True)
    interests: Mapped[str | None] = mapped_column(nullable=True)
    photo_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status_of_the_questionnaire: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
