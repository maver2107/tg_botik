from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

    @classmethod
    def get_display_name(cls, gender: "Gender") -> str:
        return "👨 Мужской" if gender == cls.MALE else "👩 Женский"
