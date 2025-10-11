from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base
from templates.sql_enums import GenderEnum


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int]
    user_gender: Mapped[GenderEnum]
    name: Mapped[str]
    age: Mapped[int]
    city: Mapped[str]
    interests: Mapped[str | None]
