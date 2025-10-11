from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    user_gender: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    age: Mapped[int] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    interests: Mapped[str | None] = mapped_column(nullable=True)
