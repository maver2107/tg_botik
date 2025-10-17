from enum import Enum


class LikeStatus(Enum):
    LIKE = "like"
    DISLIKE = "dislike"

    @classmethod
    def get_display_name(cls, status: "LikeStatus") -> str:
        if status == cls.LIKE:
            return "❤️"
        else:
            return "👎"
