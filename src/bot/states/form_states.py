from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_gender_interest = State()
    waiting_for_city = State()
    waiting_for_name = State()
    waiting_for_interests = State()
    waiting_for_photo = State()


class DatingStates(StatesGroup):
    viewing_profiles = State()
    viewing_matches = State()


class UserProfileStates(StatesGroup):
    main_menu = State()  # Главное меню профиля с кнопками
    editing_profile = State()  # Состояние редактирования анкеты
    disabling_profile = State()  # Состояние выключения профиля/подтверждение
