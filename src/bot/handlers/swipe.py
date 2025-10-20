# src/bot/handlers/swipe.py
"""
TODO для джуна: Рефакторинг архитектуры

ПРОБЛЕМЫ ТЕКУЩЕЙ АРХИТЕКТУРЫ:
1. Handler делает слишком много - нарушение Single Responsibility Principle
2. Дублирование кода отправки анкет (4 раза повторяется одна и та же логика)
3. Service занимается UI (format_profile, отправка сообщений через bot.send_message)
4. Handler напрямую обращается к DAO (matches_dao, users_dao) - нарушение слоёв
5. Бизнес-логика размазана между handler и service

ПЛАН РЕФАКТОРИНГА:
1. Создать Presenter/View слой для UI-логики:
   - Форматирование текста анкет (format_profile)
   - Отправка сообщений (send_profile, send_match_notification)
   - Создание клавиатур (можно оставить в keyboards, но использовать через presenter)

2. Очистить Service от UI:
   - Убрать format_profile() из SwipeService
   - Убрать bot.send_message() из process_like/process_dislike
   - Service должен только возвращать данные, а не отправлять сообщения
   - Вынести работу с БД-сессиями из service в DAO

3. Упростить Handler:
   - Вынести дублирующийся код отправки анкет в отдельный метод/presenter
   - Handler должен только: принять событие → вызвать service → отправить ответ через presenter
   - Убрать прямые обращения к DAO (использовать только через service)

4. Архитектура слоёв должна быть:
   Handler (контроллер) → Service (бизнес-логика) → DAO (данные)
                      ↘ Presenter (UI) ↗

ПРИМЕР ПРАВИЛЬНОЙ АРХИТЕКТУРЫ:
@swipe_router.message(Command("search"))
async def start_search(message: Message, swipe_service: SwipeService, presenter: SwipePresenter):
    user_id = message.from_user.id
    next_profile = await swipe_service.get_next_profile(user_id)

    if not next_profile:
        await presenter.send_no_profiles_message(message)
        return

    await presenter.send_profile(message, next_profile, is_first=True)
"""

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

    # TODO: ПРОБЛЕМА #1 - Handler делает UI-работу
    # Эта логика повторяется 4 раза в файле (строки 73-80, 171-178, 215-222)
    # Решение: создать SwipePresenter с методом send_profile(message, profile, state)
    profile_text = swipe_service.format_profile(next_profile)  # format_profile не должен быть в service!

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

    # TODO: ПРОБЛЕМА #2 - Service принимает bot и отправляет сообщения
    # process_like не должен отправлять уведомления! Это работа Handler или Presenter
    # Service должен только вернуть данные о мэтче, а Handler решает что с ними делать
    result = await swipe_service.process_like(from_user_id, to_user_id, bot)

    # TODO: ПРОБЛЕМА #3 - Форматирование UI в Handler + использование dict
    # Эта логика должна быть в Presenter
    #
    # ❌ ПЛОХО: result["is_match"] - можно ошибиться в названии ключа
    # ✅ ХОРОШО: result.is_match - автодополнение, проверка типов
    #
    # После рефакторинга будет:
    # result = await swipe_service.process_like(from_user_id, to_user_id)  # БЕЗ bot!
    # if result.is_match:  # Pydantic модель вместо dict
    #     await presenter.send_match_notification(callback.message, result.matched_user)
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

    # TODO: ПРОБЛЕМА #4 - Бизнес-логика в Handler
    # Определение следующей анкеты должно быть в Service, а не здесь
    # Эта логика полностью дублируется в process_dislike_callback (строки 195-204)
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

    # TODO: ПРОБЛЕМА #5 - Handler напрямую обращается к DAO!
    # Это нарушение архитектуры слоёв. Handler не должен знать о существовании DAO
    # Правильно: await swipe_service.get_user_matches(user_id)
    matches = await swipe_service.matches_dao.get_user_matches(user_id)

    if not matches:
        await message.answer("У тебя пока нет мэтчей 😔")
        return

    # TODO: ПРОБЛЕМА #6 - Форматирование и бизнес-логика в Handler
    # Получение other_user и форматирование должно быть в Service/Presenter
    matches_text = "💕 Твои мэтчи:\n\n"
    for match in matches:
        # Определяем ID второго пользователя
        other_user_id = match.user2_id if match.user1_id == user_id else match.user1_id
        other_user = await swipe_service.users_dao.get_by_tg_id(other_user_id)  # Опять прямой доступ к DAO!

        if other_user:
            username_display = (
                f"@{other_user.username}" if hasattr(other_user, "username") and other_user.username else "без username"
            )
            matches_text += f"• {other_user.name} - {username_display}\n"

    await message.answer(matches_text)
