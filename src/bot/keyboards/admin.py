from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Пользователи", callback_data="admin:users"),
        InlineKeyboardButton(text="🚨 Жалобы", callback_data="admin:reports:new"),
    )
    builder.row(InlineKeyboardButton(text="✅ Рассмотренные", callback_data="admin:reports:reviewed"))
    builder.row(InlineKeyboardButton(text="📢 Рассылка", callback_data="admin:broadcast"))
    builder.row(InlineKeyboardButton(text="❌ Выйти", callback_data="admin:exit"))
    return builder.as_markup()


def back_to_main_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_to_main")]]
    )


def user_list_keyboard(users: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for u in users:
        label = f"{u.name or 'Без имени'} ({u.age or '?'}), {'🚫' if u.is_banned else '✅'}"
        builder.row(InlineKeyboardButton(text=label, callback_data=f"admin:user:{u.tg_id}"))
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"admin:users_page:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="admin:noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"admin:users_page:{page + 1}"))
    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_to_main"))
    return builder.as_markup()


def user_detail_keyboard(tg_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_banned:
        builder.row(InlineKeyboardButton(text="✅ Разбанить", callback_data=f"admin:unban:{tg_id}"))
    else:
        builder.row(InlineKeyboardButton(text="🔨 Забанить", callback_data=f"admin:ban_confirm:{tg_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="admin:users"))
    return builder.as_markup()


def ban_confirm_keyboard(tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⚠️ Точно забанить", callback_data=f"admin:ban:{tg_id}"),
    )
    builder.row(InlineKeyboardButton(text="Отмена", callback_data=f"admin:user:{tg_id}"))
    return builder.as_markup()


def reports_list_keyboard(reports: list, page: int, total_pages: int, reviewed: bool) -> InlineKeyboardMarkup:
    prefix = "admin:reviewed_reports_page" if reviewed else "admin:new_reports_page"
    builder = InlineKeyboardBuilder()
    for r in reports:
        label = f"Жалоба #{r.id} на tg_id={r.target_user_id}"
        builder.row(InlineKeyboardButton(text=label, callback_data=f"admin:report:{r.id}"))
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{prefix}:{page - 1}"))
    nav.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="admin:noop"))
    if page < total_pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{prefix}:{page + 1}"))
    builder.row(*nav)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="admin:back_to_main"))
    return builder.as_markup()


def report_detail_keyboard(report_id: int, target_tg_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔨 Забанить юзера", callback_data=f"admin:ban:{target_tg_id}"))
    builder.row(InlineKeyboardButton(text="✅ Отклонить жалобу", callback_data=f"admin:dismiss_report:{report_id}"))
    builder.row(InlineKeyboardButton(text="◀️ Назад к списку", callback_data="admin:reports:new"))
    return builder.as_markup()


def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📤 Отправить", callback_data="admin:broadcast_send"))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="admin:back_to_main"))
    return builder.as_markup()
