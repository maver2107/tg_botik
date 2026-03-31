from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message  # Добавлен импорт

from src.bot.enum.like import ApplicationStatus, LikeStatus
from src.bot.enum.user_profile import UserProfile
from src.bot.keyboards.swipe import get_search_only_keyboard, get_show_likes_keyboard
from src.bot.presenters.swipe import SwipePresenter
from src.bot.services.swipe import SwipeService
from src.bot.states.swipe_states import SwipeStates

swipe_router = Router()


@swipe_router.message(Command("search"))
async def start_search(
    message: Message, swipe_service: SwipeService, swipe_presenter: SwipePresenter, state: FSMContext
):
    """Команда для начала просмотра анкет"""
    user_id = message.from_user.id

    # Получаем первую анкету
    next_profile = await swipe_service.get_next_profile(user_id)

    if not next_profile:
        await swipe_presenter.send_no_profiles_message(message)
        await state.clear()
        return

    # Сохраняем ID текущего профиля в состоянии
    await state.update_data(current_profile_id=next_profile.tg_id)

    # Устанавливаем состояние "обычный просмотр"
    await state.set_state(SwipeStates.normal_browsing)
    await swipe_presenter.send_profile(message, next_profile)


@swipe_router.message(F.text == UserProfile.get_button_text(UserProfile.SEARCH))
async def continue_search_after_likes(
    message: Message,
    swipe_service: SwipeService,
    swipe_presenter: SwipePresenter,
    state: FSMContext,
):
    # просто переиспользуем логику start_search
    await start_search(message, swipe_service, swipe_presenter, state)


@swipe_router.message(F.text == LikeStatus.get_display_name(LikeStatus.REPORT))
async def initiate_report_profile(
    message: Message,
    state: FSMContext,
):
    """Обработка жалобы"""
    await state.set_state(SwipeStates.reporting)
    await message.answer("Пожалуйста, оставьте комментарий к жалобе")


@swipe_router.message(SwipeStates.reporting)
async def report_profile(
    message: Message, state: FSMContext, swipe_service: SwipeService, swipe_presenter: SwipePresenter
):
    """Обработка жалобы"""
    from_user_id = message.from_user.id
    data = await state.get_data()
    to_user_id = data.get("current_profile_id")

    await state.update_data(report_comment=message.text)
    data = await state.get_data()
    report_comment = data.get("report_comment")
    if not report_comment:
        await message.answer("Пожалуйста, оставьте комментарий к жалобе")
        return
    await swipe_service.process_report(from_user_id, to_user_id, report_comment)
    await state.set_state(SwipeStates.normal_browsing)
    await message.answer("Жалоба отправлена")
    await process_dislike(message, swipe_service, swipe_presenter, state)


@swipe_router.message(F.text == ApplicationStatus.show_application(ApplicationStatus.SHOW))
async def show_who_liked_me(
    message: Message, swipe_service: SwipeService, swipe_presenter: SwipePresenter, state: FSMContext
):
    """Показать анкеты тех, кто лайкнул"""
    user_id = message.from_user.id

    # Получаем анкеты тех, кто лайкнул
    profiles = await swipe_service.get_profiles_who_liked_me(user_id)

    if not profiles:
        await message.answer("Никто пока не лайкнул твою анкету 😔")
        return

    # Устанавливаем состояние "просмотр лайкнувших"
    await state.set_state(SwipeStates.viewing_likes)

    # Сохраняем ID первого профиля
    first_profile = profiles[0]
    await state.update_data(current_profile_id=first_profile.tg_id)

    # Показываем первую анкету
    await message.answer("Смотри кто тебя лайкнул! ❤️")
    await swipe_presenter.send_profile(message, first_profile)


@swipe_router.message(F.text == ApplicationStatus.show_application(ApplicationStatus.SKIP))
async def decline_show_likes(message: Message):
    """Отказ от просмотра лайкнувших"""
    await message.answer("Хорошо, продолжай просмотр с /search", reply_markup=get_search_only_keyboard())


# TODO: Тут функция слишком много делает бизнес логики, она должна быть в сервисе, а не в handler, все параметры можно перенести в сервис
# TODO: И можно это все разбить на несколько функций, например process_like_normal_browsing и process_like_viewing_likes
@swipe_router.message(F.text == LikeStatus.get_display_name(LikeStatus.LIKE), SwipeStates.normal_browsing)
@swipe_router.message(F.text == LikeStatus.get_display_name(LikeStatus.LIKE), SwipeStates.viewing_likes)
async def process_like(
    message: Message, swipe_service: SwipeService, state: FSMContext, swipe_presenter: SwipePresenter, bot: Bot
):
    """Обработка нажатия на кнопку лайк"""
    from_user_id = message.from_user.id

    # Получаем ID текущего профиля из состояния
    data = await state.get_data()
    to_user_id = data.get("current_profile_id")

    if not to_user_id:
        await message.answer("Ошибка: профиль не найден. Начни просмотр заново с /search")
        return

    # Получаем текущее состояние
    current_state = await state.get_state()

    # Обрабатываем лайк
    result = await swipe_service.process_like(from_user_id, to_user_id)

    if result.is_match:
        # Отправляем сообщение о мэтче
        match_text = swipe_presenter.format_match_message(result.matched_user)
        await message.answer(match_text)

        # Уведомляем второго пользователя
        await bot.send_message(to_user_id, swipe_presenter.format_match_message(result.current_user))
    else:
        if result.can_notify_target:
            # Уведомление о лайке
            await bot.send_message(
                to_user_id, swipe_presenter.format_like_notification(), reply_markup=get_show_likes_keyboard()
            )

    # Определяем следующую анкету
    if current_state == SwipeStates.viewing_likes:
        profiles = await swipe_service.get_profiles_who_liked_me(from_user_id)

        if not profiles:
            # Лайкнувшие закончились
            await message.answer(
                "Анкеты тех, кто тебя лайкнул, закончились.\nХочешь продолжить просмотр новых анкет?",
                reply_markup=get_search_only_keyboard(),
            )
            await state.clear()
            return

        next_profile = profiles[0]
    else:
        next_profile = result.next_profile

    if not next_profile:
        await swipe_presenter.send_no_profiles_message(message)
        await state.clear()
        return

    await state.update_data(current_profile_id=next_profile.tg_id)
    await swipe_presenter.send_profile(message, next_profile)


# TODO: Тут так же как и писал выше, разберись с разделением логики, handler должен только координировать работу, а не делать всю бизнес логику
@swipe_router.message(F.text == LikeStatus.get_display_name(LikeStatus.DISLIKE), SwipeStates.normal_browsing)
@swipe_router.message(F.text == LikeStatus.get_display_name(LikeStatus.DISLIKE), SwipeStates.viewing_likes)
async def process_dislike(
    message: Message, swipe_service: SwipeService, swipe_presenter: SwipePresenter, state: FSMContext
):
    """Обработка нажатия на кнопку дизлайк"""
    from_user_id = message.from_user.id

    # Получаем ID текущего профиля из состояния
    data = await state.get_data()
    to_user_id = data.get("current_profile_id")

    if not to_user_id:
        await message.answer("Ошибка: профиль не найден. Начни просмотр заново с /search")
        return

    # Получаем текущее состояние
    current_state = await state.get_state()

    # Обрабатываем дизлайк
    result = await swipe_service.process_dislike(from_user_id, to_user_id)

    # Определяем следующую анкету в зависимости от состояния
    if current_state == SwipeStates.viewing_likes:
        profiles = await swipe_service.get_profiles_who_liked_me(from_user_id)

        if not profiles:
            await message.answer(
                "Анкеты тех, кто тебя лайкнул, закончились.\nХочешь продолжить просмотр новых анкет?",
                reply_markup=get_search_only_keyboard(),
            )
            await state.clear()
            return

        next_profile = profiles[0]
    else:
        next_profile = result.next_profile

    if not next_profile:
        await swipe_presenter.send_no_profiles_message(message)
        await state.clear()
        return

    # Сохраняем ID следующего профиля
    await state.update_data(current_profile_id=next_profile.tg_id)

    # Отправляем следующую анкету
    await swipe_presenter.send_profile(message, next_profile)
