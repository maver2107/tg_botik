from enum import Enum


class UserProfile(str, Enum):
    EDIT_PROFILE = "male"
    OFF_PROFILE = "female"
    SEARCH = "not important"

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
