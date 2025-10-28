# ✅ TODO для джуна: Чек-лист рефакторинга

## 🚀 Быстрый старт

1. **Прочитай** файлы в таком порядке:
   - `ARCHITECTURE_PROBLEMS.md` — что не так сейчас
   - `REFACTORING_GUIDE.md` — как исправить (главный гайд)
   - TODO-комментарии в коде

2. **Изучи** проблемы в коде:
   - `src/bot/handlers/swipe.py` — 6 помеченных проблем
   - `src/bot/services/swipe.py` — проблемы с UI в Service

3. **Делай** пошагово по REFACTORING_GUIDE.md

---

## 📝 Чек-лист задач

### Шаг 0: Создать Pydantic модели ⬜
- [✔️] Добавить в `src/bot/models/responses.py` класс `LikeProcessResult` 
- [✔️] Добавить в `src/bot/models/responses.py` класс `DislikeProcessResult` 
- [✔️] Добавить в `src/bot/models/responses.py` класс `MatchWithDetails` 
- [✔️] Добавить импорт `from datetime import datetime`
- [✔️] Настроить `model_config = {"arbitrary_types_allowed": True}` для моделей

**Зачем Pydantic модели?**
- ✅ `result.is_match` вместо `result["is_match"]` - автодополнение в IDE
- ✅ Защита от опечаток в ключах (ошибка сразу, а не в runtime)
- ✅ Проверка типов (mypy/pyright находят проблемы до запуска)
- ✅ Документирование структуры данных

### Шаг 1: Создать Presenter ⬜
- [✔️] Создать файл `src/bot/presenters/__init__.py` 
- [✔️] Создать файл `src/bot/presenters/swipe.py` 
- [✔️] Реализовать класс `SwipePresenter`
- [✔️] Добавить метод `format_profile(user, hide_name=False)` 
- [✔️] Добавить метод `send_profile(target, profile, hide_name=False)`
- [✔️] Добавить метод `format_match_message(matched_user)`
- [✔️] Добавить метод `format_like_notification()`
- [✔️] Добавить метод `send_no_profiles_message(target)`

### Шаг 2: Расширить DAO ⬜
- [✔️] В `src/bot/dao/user.py` добавить `get_next_profile(...)`
- [✔️] В `src/bot/dao/user.py` добавить `get_profiles_by_ids(...)`
- [✔️] В `src/bot/dao/like.py` добавить `get_rated_user_ids(...)`
- [✔️] В `src/bot/dao/like.py` добавить `get_users_who_liked_me(...)`
- [✔️] В `src/bot/dao/like.py` добавить `get_unrated_from_list(...)`

### Шаг 3: Очистить Service ⬜
- [✔️] Добавить импорт Pydantic моделей: `from src.bot.models.responses import LikeProcessResult, DislikeProcessResult, MatchWithDetails`
- [✔️] Удалить импорт `get_show_likes_keyboard` (строка 38)
- [✔️] Переписать `get_next_profile()` — убрать работу с БД, использовать DAO
- [✔️] Переписать `get_profiles_who_liked_me()` — убрать работу с БД
- [✔️] Переписать `process_like()`:
- [✔️] Изменить тип возврата: `-> LikeProcessResult` вместо `-> dict`
- [✔️] Удалить параметр `bot`
- [✔️] Удалить `bot.send_message()` (строки 192-208)
- [✔️] Добавить `current_user = await self.users_dao.get_by_tg_id(from_user_id)`
- [✔️] Вернуть `LikeProcessResult(...)` вместо dict
- [✔️] Переписать `process_dislike()`:
- [✔️] Изменить тип возврата: `-> DislikeProcessResult`
- [✔️] Вернуть `DislikeProcessResult(next_profile=next_profile)` вместо dict
- [✔️] Удалить метод `format_profile()` (строки 252-260)
- [✔️] Добавить новый метод `get_user_matches_with_details(user_id) -> list[MatchWithDetails]`

### Шаг 4: Упростить Handler ⬜
- [ ] Добавить импорт `from src.bot.presenters.swipe import SwipePresenter`
- [ ] В `start_search()`:
- [ ] Заменить ручную отправку на `presenter.send_profile()`
- [ ] Убрать дублирование (строки 75-82)
- [ ] В `show_who_liked_me()`:
- [ ] Заменить на `presenter.send_profile()`
- [ ] В `process_like_callback()`:
- [ ] Убрать параметр `bot` из `process_like()`
- [ ] Использовать Pydantic модель: `result.is_match` вместо `result["is_match"]`
- [ ] Использовать `result.matched_user`, `result.current_user`, `result.next_profile`
- [ ] Переместить форматирование в Presenter
- [ ] Заменить отправку анкет на `presenter.send_profile()`
- [ ] В `process_dislike_callback()`:
- [ ] Использовать Pydantic модель: `result.next_profile` вместо `result["next_profile"]`
- [ ] Заменить отправку на `presenter.send_profile()`
- [ ] В `show_matches()`:
- [ ] Убрать прямой доступ к DAO (строки 240, 252)
- [ ] Использовать `swipe_service.get_user_matches_with_details()`
- [ ] Использовать Pydantic модели: `match_data.user` вместо `match_data["user"]`
- [ ] Переместить форматирование в Presenter

### Шаг 5: Проверка ⬜
- [ ] Запустить линтер: `ruff check src/`
- [ ] Проверить что нет прямых обращений Handler → DAO
- [ ] Проверить что Service не импортирует UI (клавиатуры, aiogram кроме типов)
- [ ] Проверить что нет дублирования кода
- [ ] Запустить бота и протестировать `/search`, `/matches`
- [ ] Протестировать лайки и мэтчи

---

## 🎯 Критерии успеха

После рефакторинга код должен выглядеть так:

```python
# ✅ Правильный Handler
@swipe_router.message(Command("search"))
async def start_search(message, service, presenter, state):
    profile = await service.get_next_profile(user_id)
    if not profile:
        await presenter.send_no_profiles_message(message)
        return
    await state.set_state(SwipeStates.normal_browsing)
    await presenter.send_profile(message, profile)

# ✅ Правильный Service с Pydantic моделями
async def process_like(self, from_user_id: int, to_user_id: int) -> LikeProcessResult:
    # ... логика ...
    return LikeProcessResult(
        is_match=is_match,
        matched_user=matched_user,
        current_user=current_user,
        next_profile=next_profile
    )

# ✅ Использование в Handler
result = await service.process_like(from_user_id, to_user_id)
if result.is_match:  # Автодополнение работает!
    await presenter.send_match_notification(message, result.matched_user)
```

**Короткий, понятный, типизированный, без дублирования!**

---

## ⚠️ Частые ошибки

1. **Забыть создать `__init__.py`** в папке `presenters/`
2. **Оставить `bot` в параметрах `process_like()`**
3. **Забыть переместить логику работы с БД из Service в DAO**
4. **Не удалить старые методы** (`format_profile` из Service)
5. **Не протестировать** после рефакторинга

---

## 🆘 Если застрял

1. Перечитай TODO-комментарии в коде — там подробно написано
2. Смотри примеры кода в `REFACTORING_GUIDE.md`
3. Изучи диаграммы в `ARCHITECTURE_PROBLEMS.md`
4. Делай по одному шагу, не пытайся переделать всё сразу
5. Коммить после каждого успешного шага

---

## 📚 Что почитать

- **SOLID принципы** — основа хорошей архитектуры
- **Clean Architecture** by Robert Martin
- **Separation of Concerns** — разделение ответственности
- **MVP pattern** — Model-View-Presenter

---

**Удачи! 💪 Это отличная практика для понимания архитектуры!**

P.S. После завершения можно применить те же принципы к модулям `questionnaire` и `start` 😉

