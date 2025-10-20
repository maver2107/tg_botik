from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    SKIP_GENDER = "not important"

    @classmethod
    def get_display_name(cls, gender: "Gender") -> str:
        return "Я парень" if gender == cls.MALE else "Я девушка"

    @classmethod
    def get_display_gender_interest(cls, gender: "Gender") -> str:
        if gender == cls.MALE:
            return "Парни"
        elif gender == cls.FEMALE:
            return "Девушки"
        else:
            return "Все равно"
