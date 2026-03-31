from enum import Enum


class LikeStatus(Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    REPORT = "report"

    @classmethod
    def get_display_name(cls, status: "LikeStatus") -> str:
        if status == cls.LIKE:
            return "❤️"
        if status == cls.REPORT:
            return "🚩"
        else:
            return "👎"


class ApplicationStatus(Enum):
    SHOW = "show"
    SKIP = "skip"

    @classmethod
    def show_application(cls, status: "ApplicationStatus") -> str:
        if status == cls.SHOW:
            return "✅ Да, показать!"
        else:
            return "❌ Нет, спасибо"
