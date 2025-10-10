from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Users(Base):
    __tablename__ = "users"

    id = Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id = Mapped[int]
    name = Mapped[str]
    age = Mapped[int]
    about_user = Mapped[str]
