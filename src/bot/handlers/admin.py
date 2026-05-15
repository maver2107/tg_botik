import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards import admin as kb
from src.bot.services.admin import AdminService
from src.bot.states.admin_states import AdminStates

logger = logging.getLogger(__name__)

admin_router = Router()


def is_admin(tg_id: int, admin_ids: list[int]) -> bool:
    return tg_id in admin_ids


@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, admin_ids: list[int], admin_service: AdminService):
    if not is_admin(message.from_user.id, admin_ids):
        return
    await state.set_state(AdminStates.main)
    await message.answer("🔧 Админ-панель", reply_markup=kb.admin_main_menu())


# ---------- main menu ----------

@admin_router.callback_query(F.data == "admin:back_to_main", AdminStates.main)
@admin_router.callback_query(F.data == "admin:back_to_main")
async def back_to_main(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.main)
    await call.message.edit_text("🔧 Админ-панель", reply_markup=kb.admin_main_menu())  # type: ignore


@admin_router.callback_query(F.data == "admin:exit")
async def exit_admin(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Выход из админ-панели.")  # type: ignore


@admin_router.callback_query(F.data == "admin:noop")
async def noop(call: CallbackQuery):
    await call.answer()


# ---------- users ----------

@admin_router.callback_query(F.data == "admin:users")
async def show_users(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    await state.set_state(AdminStates.users_menu)
    users, page, total_pages = await admin_service.get_users_page(1)
    if not users:
        await call.message.edit_text("Нет пользователей.", reply_markup=kb.back_to_main_button())  # type: ignore
        return
    await call.message.edit_text(  # type: ignore
        "👥 Список пользователей:", reply_markup=kb.user_list_keyboard(users, page, total_pages)
    )


@admin_router.callback_query(F.data.startswith("admin:users_page:"), AdminStates.users_menu)
async def users_page(call: CallbackQuery, admin_service: AdminService):
    page = int(call.data.split(":")[-1])
    users, page, total_pages = await admin_service.get_users_page(page)
    await call.message.edit_text(  # type: ignore
        "👥 Список пользователей:", reply_markup=kb.user_list_keyboard(users, page, total_pages)
    )


@admin_router.callback_query(F.data.startswith("admin:user:"), AdminStates.users_menu)
@admin_router.callback_query(F.data.startswith("admin:user:"), AdminStates.user_ban_confirm)
async def show_user_detail(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    tg_id = int(call.data.split(":")[-1])
    user = await admin_service.get_user_detail(tg_id)
    if not user:
        await call.answer("Пользователь не найден.", show_alert=True)
        return
    await state.set_state(AdminStates.user_detail)
    await state.update_data(viewed_tg_id=tg_id)
    lines = [
        f"👤 <b>{user.name or 'Без имени'}</b>",
        f"ID: <code>{user.id}</code> | tg_id: <code>{user.tg_id}</code>",
        f"Возраст: {user.age or '?'} | Пол: {user.user_gender or '?'}",
        f"Город: {user.city or '?'} | Интересы: {user.interests or '?'}",
        f"Username: @{user.username or '—'}",
        f"Анкета: {'активна' if user.status_of_the_questionnaire else 'скрыта'}",
        f"Забанен: {'🚫 Да' if user.is_banned else '✅ Нет'}",
    ]
    await call.message.edit_text("\n".join(lines), reply_markup=kb.user_detail_keyboard(tg_id, user.is_banned))  # type: ignore


@admin_router.callback_query(F.data.startswith("admin:ban_confirm:"), AdminStates.user_detail)
async def ban_confirm(call: CallbackQuery, state: FSMContext):
    tg_id = int(call.data.split(":")[-1])
    await state.set_state(AdminStates.user_ban_confirm)
    await call.message.edit_text(  # type: ignore
        f"⚠️ Вы уверены, что хотите забанить пользователя <code>{tg_id}</code>?",
        reply_markup=kb.ban_confirm_keyboard(tg_id),
    )


@admin_router.callback_query(F.data.startswith("admin:ban:"), AdminStates.user_ban_confirm)
@admin_router.callback_query(F.data.startswith("admin:ban:"), AdminStates.report_detail)
async def ban_user(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    tg_id = int(call.data.split(":")[-1])
    await admin_service.ban_user(tg_id)
    await call.answer(f"Пользователь {tg_id} забанен.", show_alert=True)
    user = await admin_service.get_user_detail(tg_id)
    await state.set_state(AdminStates.user_detail)
    await state.update_data(viewed_tg_id=tg_id)
    if user:
        lines = [
            f"👤 <b>{user.name or 'Без имени'}</b>",
            f"ID: <code>{user.id}</code> | tg_id: <code>{user.tg_id}</code>",
            f"Забанен: {'🚫 Да' if user.is_banned else '✅ Нет'}",
        ]
        await call.message.edit_text("\n".join(lines), reply_markup=kb.user_detail_keyboard(tg_id, user.is_banned))  # type: ignore


@admin_router.callback_query(F.data.startswith("admin:unban:"), AdminStates.user_detail)
async def unban_user(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    tg_id = int(call.data.split(":")[-1])
    await admin_service.unban_user(tg_id)
    await call.answer(f"Пользователь {tg_id} разбанен.", show_alert=True)
    user = await admin_service.get_user_detail(tg_id)
    await state.update_data(viewed_tg_id=tg_id)
    if user:
        lines = [
            f"👤 <b>{user.name or 'Без имени'}</b>",
            f"ID: <code>{user.id}</code> | tg_id: <code>{user.tg_id}</code>",
            f"Забанен: {'🚫 Да' if user.is_banned else '✅ Нет'}",
        ]
        await call.message.edit_text("\n".join(lines), reply_markup=kb.user_detail_keyboard(tg_id, user.is_banned))  # type: ignore


# ---------- reports ----------

@admin_router.callback_query(F.data == "admin:reports")
async def show_reports(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    await state.set_state(AdminStates.reports_menu)
    reports, page, total_pages = await admin_service.get_reports_page(1)
    if not reports:
        await call.message.edit_text("Нет жалоб.", reply_markup=kb.back_to_main_button())  # type: ignore
        return
    await call.message.edit_text(  # type: ignore
        "🚨 Список жалоб:", reply_markup=kb.reports_list_keyboard(reports, page, total_pages)
    )


@admin_router.callback_query(F.data.startswith("admin:reports_page:"), AdminStates.reports_menu)
async def reports_page(call: CallbackQuery, admin_service: AdminService):
    page = int(call.data.split(":")[-1])
    reports, page, total_pages = await admin_service.get_reports_page(page)
    await call.message.edit_text(  # type: ignore
        "🚨 Список жалоб:", reply_markup=kb.reports_list_keyboard(reports, page, total_pages)
    )


@admin_router.callback_query(F.data.startswith("admin:report:"), AdminStates.reports_menu)
async def show_report_detail(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    report_id = int(call.data.split(":")[-1])
    report = await admin_service.get_report_detail(report_id)
    if not report:
        await call.answer("Жалоба не найдена.", show_alert=True)
        return
    await state.set_state(AdminStates.report_detail)
    await state.update_data(viewed_report_id=report_id)
    lines = [
        f"🚨 <b>Жалоба #{report.id}</b>",
        f"От: <code>{report.reporter_user_id}</code>",
        f"На: <code>{report.target_user_id}</code>",
        f"Комментарий: {report.comment or '—'}",
        f"Создана: {report.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"Рассмотрена: {'✅ Да' if report.reviewed_at else '❌ Нет'}",
    ]
    await call.message.edit_text("\n".join(lines), reply_markup=kb.report_detail_keyboard(report.id, report.target_user_id))  # type: ignore


@admin_router.callback_query(F.data.startswith("admin:dismiss_report:"), AdminStates.report_detail)
async def dismiss_report(call: CallbackQuery, admin_service: AdminService):
    report_id = int(call.data.split(":")[-1])
    await admin_service.dismiss_report(report_id)
    await call.answer("Жалоба отклонена.", show_alert=True)
    reports, page, total_pages = await admin_service.get_reports_page(1)
    await call.message.edit_text(  # type: ignore
        "🚨 Список жалоб:", reply_markup=kb.reports_list_keyboard(reports, page, total_pages)
    )


# ---------- broadcast ----------

@admin_router.callback_query(F.data == "admin:broadcast")
async def broadcast_start(call: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.broadcast_text)
    await call.message.edit_text(  # type: ignore
        "📢 Введите текст рассылки. Он будет отправлен всем пользователям бота.\n\n"
        "Для отмены нажмите кнопку ниже.",
        reply_markup=kb.back_to_main_button(),
    )


@admin_router.message(AdminStates.broadcast_text)
async def broadcast_preview(message: Message, state: FSMContext):
    text = message.text or message.caption or ""
    if not text.strip():
        await message.answer("Текст не может быть пустым. Введите текст рассылки.")
        return
    await state.set_state(AdminStates.broadcast_confirm)
    await state.update_data(broadcast_text=text)
    await message.answer(
        f"📢 <b>Превью рассылки:</b>\n\n{text}\n\nОтправить всем пользователям?",
        reply_markup=kb.broadcast_confirm_keyboard(),
    )


@admin_router.callback_query(F.data == "admin:broadcast_send", AdminStates.broadcast_confirm)
async def broadcast_send(call: CallbackQuery, state: FSMContext, admin_service: AdminService):
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    await call.answer("Рассылка началась...", show_alert=True)
    sent, failed = await admin_service.broadcast(call.message.bot, text)  # type: ignore
    await state.set_state(AdminStates.main)
    await call.message.edit_text(  # type: ignore
        f"📢 Рассылка завершена.\n\nОтправлено: {sent}\nНе удалось: {failed}",
        reply_markup=kb.admin_main_menu(),
    )
