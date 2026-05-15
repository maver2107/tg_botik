from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    main = State()
    users_menu = State()
    user_detail = State()
    user_ban_confirm = State()
    reports_menu = State()
    report_detail = State()
    broadcast_text = State()
    broadcast_confirm = State()
