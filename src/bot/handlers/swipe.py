# src/bot/handlers/swipe.py
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.bot.keyboards.swipe import get_swipe_keyboard
from src.bot.services.swipe import SwipeService
from src.bot.states.swipe_states import SwipeStates

swipe_router = Router()


@swipe_router.message(Command("search"))
async def start_search(message: Message, swipe_service: SwipeService, state: FSMContext):
    """Команда для начала просмотра анкет"""
    user_id = message.from_user.id

    # Получаем первую анкету
    next_profile = await swipe_service.get_next_profile(user_id)

    if not next_profile:
        await message.answer("😔 К сожалению, подходящих анкет пока нет. Попробуй позже!")
        return

    # Устанавливаем состояние "обычный просмотр"
    await state.set_state(SwipeStates.normal_browsing)

    # Отправляем анкету
    profile_text = swipe_service.format_profile(next_profile)

    if next_profile.photo_id:
        await message.answer_photo(
            photo=next_profile.photo_id, caption=profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id)
        )
    else:
        await message.answer(profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id))


@swipe_router.callback_query(F.data == "show_likes_yes")
async def show_who_liked_me(callback: CallbackQuery, swipe_service: SwipeService, state: FSMContext):
    """Показать анкеты тех, кто лайкнул"""
    user_id = callback.from_user.id

    # Получаем анкеты тех, кто лайкнул
    profiles = await swipe_service.get_profiles_who_liked_me(user_id)

    if not profiles:
        await callback.message.edit_text("Никто пока не лайкнул твою анкету 😔")
        await callback.answer()
        return

    # Устанавливаем состояние "просмотр лайкнувших"
    await state.set_state(SwipeStates.viewing_likes)

    # Показываем первую анкету из лайкнувших (БЕЗ имени)
    first_profile = profiles[0]
    profile_text = swipe_service.format_profile(first_profile)

    if first_profile.photo_id:
        await callback.message.answer_photo(
            photo=first_profile.photo_id, caption=profile_text, reply_markup=get_swipe_keyboard(first_profile.tg_id)
        )
    else:
        await callback.message.answer(profile_text, reply_markup=get_swipe_keyboard(first_profile.tg_id))

    await callback.message.delete()
    await callback.answer("Смотри кто тебя лайкнул! ❤️")


@swipe_router.callback_query(F.data == "show_likes_no")
async def decline_show_likes(callback: CallbackQuery):
    """Отказ от просмотра лайкнувших"""
    await callback.message.edit_text("Хорошо, продолжай просмотр с /search")
    await callback.answer()


@swipe_router.callback_query(F.data.startswith("like_"))
async def process_like_callback(callback: CallbackQuery, swipe_service: SwipeService, state: FSMContext, bot: Bot):
    """Обработка нажатия на кнопку лайк"""
    to_user_id = int(callback.data.split("_")[1])
    from_user_id = callback.from_user.id

    await callback.message.edit_reply_markup(reply_markup=None)

    # Получаем текущее состояние
    current_state = await state.get_state()

    # Обрабатываем лайк
    result = await swipe_service.process_like(from_user_id, to_user_id, bot)

    # Если мэтч - показываем username
    if result["is_match"]:
        matched_user = result["matched_user"]
        username_display = (
            f"@{matched_user.username}"
            if hasattr(matched_user, "username") and matched_user.username
            else "без username"
        )

        await callback.message.answer(
            f"🔥 Взаимная симпатия!\n\n"
            f"Вы понравились друг другу!\n"
            f"Контакт: {username_display}\n\n"
            f"Можете начать общение! 💬"
        )

    # Определяем следующую анкету в зависимости от состояния
    if current_state == SwipeStates.viewing_likes:
        # Если смотрели лайкнувших - показываем следующего из них
        profiles = await swipe_service.get_profiles_who_liked_me(from_user_id)
        next_profile = profiles[0] if profiles else await swipe_service.get_next_profile(from_user_id)
        hide_name = bool(profiles)
    else:
        # Обычный просмотр
        next_profile = result["next_profile"]
        hide_name = False

    if not next_profile:
        await callback.message.answer("😔 Анкеты закончились! Попробуй позже.")
        await state.clear()
        await callback.answer()
        return

    # Отправляем следующую анкету
    profile_text = swipe_service.format_profile(next_profile, hide_name=hide_name)

    if next_profile.photo_id:
        await callback.message.answer_photo(
            photo=next_profile.photo_id, caption=profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id)
        )
    else:
        await callback.message.answer(profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id))

    await callback.answer("❤️ Лайк отправлен!")


@swipe_router.callback_query(F.data.startswith("dislike_"))
async def process_dislike_callback(callback: CallbackQuery, swipe_service: SwipeService, state: FSMContext):
    """Обработка нажатия на кнопку дизлайк"""
    to_user_id = int(callback.data.split("_")[1])
    from_user_id = callback.from_user.id

    await callback.message.edit_reply_markup(reply_markup=None)

    # Получаем текущее состояние
    current_state = await state.get_state()

    # Обрабатываем дизлайк
    result = await swipe_service.process_dislike(from_user_id, to_user_id)

    # Определяем следующую анкету в зависимости от состояния
    if current_state == SwipeStates.viewing_likes:
        # Если смотрели лайкнувших - показываем следующего из них
        profiles = await swipe_service.get_profiles_who_liked_me(from_user_id)
        next_profile = profiles[0] if profiles else await swipe_service.get_next_profile(from_user_id)
        hide_name = bool(profiles)
    else:
        # Обычный просмотр
        next_profile = result["next_profile"]
        hide_name = False

    if not next_profile:
        await callback.message.answer("😔 Анкеты закончились! Попробуй позже.")
        await state.clear()
        await callback.answer()
        return

    # Отправляем следующую анкету
    profile_text = swipe_service.format_profile(next_profile, hide_name=hide_name)

    if next_profile.photo_id:
        await callback.message.answer_photo(
            photo=next_profile.photo_id, caption=profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id)
        )
    else:
        await callback.message.answer(profile_text, reply_markup=get_swipe_keyboard(next_profile.tg_id))

    await callback.answer("👎 Пропущено")


@swipe_router.message(Command("matches"))
async def show_matches(message: Message, swipe_service: SwipeService):
    """Показать список мэтчей с username"""
    user_id = message.from_user.id
    matches = await swipe_service.matches_dao.get_user_matches(user_id)

    if not matches:
        await message.answer("У тебя пока нет мэтчей 😔")
        return

    matches_text = "💕 Твои мэтчи:\n\n"
    for match in matches:
        # Определяем ID второго пользователя
        other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
        other_user = await swipe_service.users_dao.get_by_tg_id(other_user_id)

        if other_user:
            username_display = (
                f"@{other_user.username}" if hasattr(other_user, "username") and other_user.username else "без username"
            )
            matches_text += f"• {other_user.name} - {username_display}\n"

    await message.answer(matches_text)
