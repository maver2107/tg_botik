from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_gender = State()
    waiting_for_gender_interest = State()
    waiting_for_city = State()
    waiting_for_name = State()
    waiting_for_interests = State()
    waiting_for_photo = State()
