# 🔴 Проблемы текущей архитектуры

## Текущая архитектура (НЕПРАВИЛЬНО):

```
┌──────────────────────────────────────────────────────┐
│                   Handler                             │
│                                                       │
│  ❌ Форматирует UI (format_profile)                  │
│  ❌ Отправляет сообщения (answer_photo, answer)      │
│  ❌ Бизнес-логика (определение next_profile)         │
│  ❌ Обращается к DAO напрямую (matches_dao.get...)   │
│  ❌ Дублирует код отправки анкет (4 раза!)          │
│                                                       │
└───────────────┬──────────────────┬────────────────────┘
                │                  │
                │                  └──────────┐
                ↓                             ↓
┌───────────────────────────────┐   ┌─────────────────┐
│         Service                │   │      DAO        │
│                                │   │                 │
│  ❌ Форматирует UI            │   │  ✅ Запросы БД  │
│  ❌ Импортирует клавиатуры     │   └─────────────────┘
│  ❌ Отправляет bot.send_message│
│  ❌ Создаёт БД-сессии          │
│  ✅ Бизнес-логика (мэтчи)      │
│                                │
└────────────────────────────────┘
```

### Проблемы:

1. **Handler делает ВСЁ** — UI + логика + обращение к DAO
2. **Service отправляет сообщения** — нарушение слоёв
3. **Нет Presenter** — форматирование размазано по Handler и Service
4. **Дублирование кода** — логика отправки анкет повторяется 4 раза
5. **Handler ↔ DAO напрямую** — обход Service (строка 240, 252 в swipe.py)

---

## Целевая архитектура (ПРАВИЛЬНО):

```
┌────────────────────────────────────────────────────────┐
│                    Handler (Controller)                 │
│                                                         │
│  ✅ Принимает события Telegram                         │
│  ✅ Валидирует данные                                  │
│  ✅ Управляет FSM состояниями                          │
│  ✅ Координирует Service + Presenter                   │
│  ✅ Обрабатывает исключения                            │
│  ❌ НЕ форматирует UI                                  │
│  ❌ НЕ обращается к DAO напрямую                       │
│                                                         │
└────────────┬───────────────────┬────────────────────────┘
             │                   │
             ↓                   ↓
┌──────────────────────┐   ┌─────────────────────────────┐
│      Service         │   │       Presenter (View)       │
│                      │   │                              │
│  ✅ Бизнес-правила   │   │  ✅ Форматирование текста    │
│  ✅ Координирует DAO │   │  ✅ Отправка в Telegram      │
│  ✅ Проверка мэтчей  │   │  ✅ Создание клавиатур       │
│  ✅ Возвращает данные│   │  ✅ Обработка UI-логики      │
│  ❌ НЕ шлёт сообщения│   │  ❌ НЕ знает о бизнес-логике│
│  ❌ НЕ форматирует UI│   │                              │
│                      │   └─────────────────────────────┘
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│         DAO          │
│                      │
│  ✅ Запросы к БД     │
│  ✅ Управление       │
│     сессиями         │
│  ✅ CRUD операции    │
│  ❌ НЕ содержит      │
│     бизнес-логику    │
│                      │
└──────────────────────┘
```

---

## 📊 Сравнение: До и После

### ❌ До рефакторинга:

```python
# Handler делает ВСЁ
@swipe_router.message(Command("search"))
async def start_search(message: Message, swipe_service: SwipeService):
    # ...
    profile_text = swipe_service.format_profile(next_profile)  # Service форматирует UI
    
    if next_profile.photo_id:  # Handler решает как отправить
        await message.answer_photo(...)  # Handler отправляет
    else:
        await message.answer(...)  # Дублирование логики
```

```python
# Service отправляет сообщения!
async def process_like(self, from_user_id, to_user_id, bot) -> dict:  # bot в Service!
    # ...
    await bot.send_message(to_user_id, "🔥 Мэтч!")  # ❌ UI в Service
    await bot.send_message(to_user_id, "❤️", reply_markup=keyboard)  # ❌
    
    return {"is_match": True, "matched_user": user}  # ❌ dict без типизации
```

```python
# Handler использует dict - легко ошибиться
result = await service.process_like(from_user_id, to_user_id, bot)
if result["is_match"]:  # ❌ Опечатка в ключе найдётся только в runtime
    user = result["matced_user"]  # ❌ Опечатка! KeyError в продакшене
```

### ✅ После рефакторинга:

```python
# Handler координирует, не делает всё
@swipe_router.message(Command("search"))
async def start_search(
    message: Message, 
    swipe_service: SwipeService,
    presenter: SwipePresenter  # Presenter для UI
):
    next_profile = await swipe_service.get_next_profile(user_id)  # Только данные
    
    if not next_profile:
        await presenter.send_no_profiles_message(message)  # Presenter решает как
        return
    
    await presenter.send_profile(message, next_profile)  # Вся UI-логика в Presenter
```

```python
# Pydantic модели вместо dict
class LikeProcessResult(BaseModel):
    """Типизированный результат обработки лайка"""
    model_config = {"arbitrary_types_allowed": True}
    
    is_match: bool
    matched_user: Users | None
    current_user: Users
    next_profile: Users | None
```

```python
# Service возвращает типизированные данные, не отправляет
async def process_like(
    self, 
    from_user_id: int, 
    to_user_id: int
) -> LikeProcessResult:  # ✅ Pydantic модель вместо dict!
    # ... бизнес-логика ...
    
    return LikeProcessResult(  # ✅ Типизированный результат
        is_match=is_match,
        matched_user=matched_user,
        current_user=current_user,
        next_profile=next_profile
    )
```

```python
# Handler использует Pydantic модель - безопасно и удобно
result = await service.process_like(from_user_id, to_user_id)  # БЕЗ bot!
if result.is_match:  # ✅ Автодополнение в IDE
    user = result.matched_user  # ✅ Проверка типов, нет опечаток
    await presenter.send_match_notification(message, user)
```

```python
# Presenter занимается только UI
class SwipePresenter:
    @staticmethod
    async def send_profile(target, profile: Users):
        """Вся логика отправки в одном месте"""
        text = SwipePresenter.format_profile(profile)
        keyboard = get_swipe_keyboard(profile.tg_id)
        
        if profile.photo_id:
            await target.answer_photo(photo=profile.photo_id, caption=text, reply_markup=keyboard)
        else:
            await target.answer(text, reply_markup=keyboard)
```

---

## 🎯 Преимущества правильной архитектуры

| Проблема | До | После |
|----------|-----|--------|
| **Тестируемость** | Handler зависит от Telegram, тяжело тестировать | Service можно тестировать отдельно |
| **Дублирование** | Код отправки анкет повторяется 4 раза | Единственный метод `presenter.send_profile()` |
| **Изменение UI** | Менять в 4+ местах | Менять в одном Presenter |
| **Изменение логики** | Размазана по Handler и Service | Только в Service |
| **Понимание кода** | Сложно, всё смешано | Легко, чёткие границы |
| **Типизация** | `result["is_match"]` - опечатки в runtime | `result.is_match` - проверка в IDE |
| **Автодополнение** | Не работает для dict | Работает для Pydantic моделей |

## 💎 Преимущества Pydantic моделей над dict

### ❌ Проблемы с dict:

```python
# Service возвращает dict
def process_like(...) -> dict:
    return {"is_match": True, "matched_user": user}

# Handler использует - ошибок не видно!
result = await service.process_like(...)
if result["is_mach"]:  # ❌ Опечатка! Найдётся только в runtime
    user = result["mathed_user"]  # ❌ Опечатка! KeyError!
```

**Проблемы:**
- 🔴 Опечатки в ключах найдутся только при запуске
- 🔴 IDE не подсказывает доступные ключи
- 🔴 Mypy/Pyright не могут проверить типы
- 🔴 Непонятно что возвращает метод без документации

### ✅ Решение - Pydantic модели:

```python
# Определяем структуру данных
class LikeProcessResult(BaseModel):
    is_match: bool
    matched_user: Users | None
    current_user: Users
    next_profile: Users | None

# Service возвращает типизированный результат
def process_like(...) -> LikeProcessResult:
    return LikeProcessResult(
        is_match=True,
        matched_user=user,
        current_user=current,
        next_profile=next_p
    )

# Handler использует - безопасно!
result = await service.process_like(...)
if result.is_match:  # ✅ Автодополнение работает
    user = result.matched_user  # ✅ Проверка типов
```

**Преимущества:**
- ✅ Опечатки найдутся сразу (IDE подсветит красным)
- ✅ Автодополнение - IDE показывает все поля
- ✅ Проверка типов - `result.is_match` гарантированно bool
- ✅ Документирование - структура данных явно описана
- ✅ Рефакторинг - легко найти все использования поля

---

## 📋 Как проверить что рефакторинг выполнен правильно

### ✅ Handler должен:
- [ ] Быть коротким (20-30 строк на функцию)
- [ ] Только вызывать Service и Presenter
- [ ] НЕ содержать бизнес-логику
- [ ] НЕ форматировать текст
- [ ] НЕ обращаться к DAO напрямую

### ✅ Service должен:
- [ ] НЕ импортировать aiogram (кроме типов)
- [ ] НЕ принимать `bot` как параметр
- [ ] НЕ отправлять сообщения
- [ ] НЕ форматировать UI
- [ ] Возвращать Pydantic модели (не dict!)
- [ ] Только координировать DAO и возвращать данные

### ✅ Presenter должен:
- [ ] Содержать всю UI-логику
- [ ] Форматировать тексты
- [ ] Отправлять сообщения
- [ ] НЕ содержать бизнес-логику
- [ ] НЕ обращаться к БД

### ✅ DAO должен:
- [ ] Только работать с БД
- [ ] Управлять сессиями
- [ ] НЕ содержать бизнес-логику
- [ ] НЕ знать о Telegram

---

## 📚 Принципы которые нарушены в текущем коде

1. **Single Responsibility Principle** — Handler делает слишком много
2. **Separation of Concerns** — UI и бизнес-логика смешаны
3. **Don't Repeat Yourself** — код отправки повторяется
4. **Dependency Inversion** — Handler зависит от конкретных DAO
5. **Interface Segregation** — Service знает о деталях UI

---

**Изучи TODO-комментарии в коде и следуй REFACTORING_GUIDE.md!** 🚀

