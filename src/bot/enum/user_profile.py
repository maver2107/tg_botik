from enum import Enum


class UserProfile(str, Enum):
    EDIT_PROFILE = "edit_profile"
    OFF_PROFILE = "off_profile"
    SEARCH = "search_profiles"

    @classmethod
    def get_button_text(cls, profile_action: "UserProfile") -> str:
        if profile_action == cls.EDIT_PROFILE:
            return "📝 Изменить анкету"
        elif profile_action == cls.OFF_PROFILE:
            return "🚫 Выключить профиль"
        elif profile_action == cls.SEARCH:
            return "👀 Смотреть анкеты"
