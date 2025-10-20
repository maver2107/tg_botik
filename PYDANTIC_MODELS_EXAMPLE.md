# 💎 Pydantic модели - Примеры для джуна

## Зачем нужны Pydantic модели?

### ❌ Проблема с dict:

```python
# Service возвращает обычный dict
async def process_like(self, from_user_id: int, to_user_id: int) -> dict:
    return {
        "is_match": True,
        "matched_user": user,
        "next_profile": next_profile
    }

# Handler использует
result = await service.process_like(user_id, target_id)

# ПРОБЛЕМА #1: Опечатки в ключах
if result["is_mach"]:  # ❌ Опечатка! Найдётся только в runtime - KeyError
    print("Match!")

# ПРОБЛЕМА #2: Нет автодополнения
result[""]  # ❌ IDE не знает какие ключи доступны

# ПРОБЛЕМА #3: Нет проверки типов
user_id = result["is_match"]  # ❌ Присваиваем bool в переменную для ID - ошибка логики!

# ПРОБЛЕМА #4: Неясная структура
# Нужно смотреть в код Service чтобы понять какие ключи возвращаются
```

### ✅ Решение - Pydantic модели:

```python
from pydantic import BaseModel
from src.bot.models.user import Users

# Определяем структуру данных ЯВНО
class LikeProcessResult(BaseModel):
    """Результат обработки лайка"""
    model_config = {"arbitrary_types_allowed": True}  # Разрешаем SQLAlchemy модели
    
    is_match: bool
    matched_user: Users | None
    current_user: Users
    next_profile: Users | None

# Service возвращает типизированный результат
async def process_like(
    self, 
    from_user_id: int, 
    to_user_id: int
) -> LikeProcessResult:  # ✅ Явно указываем тип возврата
    return LikeProcessResult(
        is_match=True,
        matched_user=user,
        current_user=current,
        next_profile=next_p
    )

# Handler использует
result = await service.process_like(user_id, target_id)

# ✅ ПРЕИМУЩЕСТВО #1: Автодополнение
if result.is_match:  # ✅ IDE подсказывает все поля при вводе result.
    print("Match!")

# ✅ ПРЕИМУЩЕСТВО #2: Проверка в IDE
if result.is_mach:  # ✅ IDE подсветит красным - такого поля нет!

# ✅ ПРЕИМУЩЕСТВО #3: Проверка типов
user_id: int = result.is_match  # ✅ Mypy/Pyright найдут ошибку типов

# ✅ ПРЕИМУЩЕСТВО #4: Документирование
# Достаточно посмотреть на LikeProcessResult чтобы понять структуру
```

---

## 📝 Создание Pydantic моделей для swipe

### Шаг 1: Добавь модели в `src/bot/models/responses.py`

```python
# src/bot/models/responses.py
from datetime import datetime
from pydantic import BaseModel
from src.bot.models.user import Users


class BaseResponse(BaseModel):
    """Базовая модель ответа"""
    success: bool
    message: str


class AgeResponse(BaseResponse):
    """Ответ для обработки возраста"""
    pass


class GenderResponse(BaseResponse):
    """Ответ для обработки пола"""
    pass


# ============= НОВЫЕ МОДЕЛИ ДЛЯ SWIPE =============

class LikeProcessResult(BaseModel):
    """
    Результат обработки лайка
    
    Возвращается из SwipeService.process_like()
    Содержит всю информацию о результате лайка:
    - Произошёл ли мэтч
    - Данные пользователя с которым мэтч (если есть)
    - Данные текущего пользователя
    - Следующая анкета для показа
    """
    model_config = {"arbitrary_types_allowed": True}
    
    is_match: bool  # Произошёл ли взаимный лайк (мэтч)
    matched_user: Users | None  # Пользователь с которым мэтч (None если не мэтч)
    current_user: Users  # Текущий пользователь (для отправки уведомления)
    next_profile: Users | None  # Следующая анкета для показа


class DislikeProcessResult(BaseModel):
    """
    Результат обработки дизлайка
    
    Возвращается из SwipeService.process_dislike()
    Просто содержит следующую анкету
    """
    model_config = {"arbitrary_types_allowed": True}
    
    next_profile: Users | None  # Следующая анкета для показа


class MatchWithDetails(BaseModel):
    """
    Мэтч с дополнительной информацией
    
    Используется для отображения списка мэтчей
    Содержит данные пользователя и дату мэтча
    """
    model_config = {"arbitrary_types_allowed": True}
    
    user: Users  # Пользователь с которым мэтч
    match_date: datetime | None = None  # Дата создания мэтча (опционально)
```

### Шаг 2: Используй модели в Service

```python
# src/bot/services/swipe.py
from src.bot.models.responses import LikeProcessResult, DislikeProcessResult, MatchWithDetails

class SwipeService:
    # ...
    
    async def process_like(
        self, 
        from_user_id: int, 
        to_user_id: int
    ) -> LikeProcessResult:  # ✅ Указываем тип возврата
        """Обработать лайк"""
        await self.likes_dao.add_like(from_user_id, to_user_id, is_like=True)
        is_match = await self.likes_dao.check_mutual_like(from_user_id, to_user_id)
        
        matched_user = None
        current_user = await self.users_dao.get_by_tg_id(from_user_id)
        
        if is_match:
            await self.matches_dao.create_match(from_user_id, to_user_id)
            matched_user = await self.users_dao.get_by_tg_id(to_user_id)
        
        next_profile = await self.get_next_profile(from_user_id)
        
        # ✅ Возвращаем Pydantic модель
        return LikeProcessResult(
            is_match=is_match,
            matched_user=matched_user,
            current_user=current_user,
            next_profile=next_profile
        )
    
    async def process_dislike(
        self, 
        from_user_id: int, 
        to_user_id: int
    ) -> DislikeProcessResult:  # ✅ Указываем тип возврата
        """Обработать дизлайк"""
        await self.likes_dao.add_like(from_user_id, to_user_id, is_like=False)
        next_profile = await self.get_next_profile(from_user_id)
        
        # ✅ Возвращаем Pydantic модель
        return DislikeProcessResult(next_profile=next_profile)
    
    async def get_user_matches_with_details(
        self, 
        user_id: int
    ) -> list[MatchWithDetails]:  # ✅ Список Pydantic моделей
        """Получить мэтчи с деталями"""
        matches = await self.matches_dao.get_user_matches(user_id)
        result = []
        
        for match in matches:
            other_id = match.user2_id if match.user1_id == user_id else match.user1_id
            other_user = await self.users_dao.get_by_tg_id(other_id)
            
            if other_user:
                # ✅ Добавляем Pydantic модель
                result.append(
                    MatchWithDetails(
                        user=other_user,
                        match_date=match.created_at
                    )
                )
        
        return result
```

### Шаг 3: Используй модели в Handler

```python
# src/bot/handlers/swipe.py

@swipe_router.callback_query(F.data.startswith("like_"))
async def process_like_callback(
    callback: CallbackQuery,
    swipe_service: SwipeService,
    presenter: SwipePresenter,
    state: FSMContext
):
    to_user_id = int(callback.data.split("_")[1])
    from_user_id = callback.from_user.id
    
    # Обрабатываем лайк - получаем Pydantic модель
    result = await swipe_service.process_like(from_user_id, to_user_id)
    
    # ✅ Используем поля модели - автодополнение работает!
    if result.is_match:
        # ✅ result.matched_user автоматически типизирован как Users | None
        await presenter.send_match_notification(
            callback.message, 
            result.matched_user
        )
    
    # ✅ result.next_profile тоже типизирован
    if result.next_profile:
        await presenter.send_profile(callback, result.next_profile)
    else:
        await callback.message.answer("Анкеты закончились!")


@swipe_router.message(Command("matches"))
async def show_matches(
    message: Message,
    swipe_service: SwipeService,
    presenter: SwipePresenter
):
    # Получаем список Pydantic моделей
    matches = await swipe_service.get_user_matches_with_details(message.from_user.id)
    
    if not matches:
        await message.answer("У тебя пока нет мэтчей 😔")
        return
    
    matches_text = "💕 Твои мэтчи:\n\n"
    
    # ✅ match_data это MatchWithDetails - автодополнение работает!
    for match_data in matches:
        user = match_data.user  # ✅ .user вместо ["user"]
        username = f"@{user.username}" if user.username else "без username"
        matches_text += f"• {user.name} - {username}\n"
    
    await message.answer(matches_text)
```

---

## 🔧 Важные моменты

### 1. `model_config = {"arbitrary_types_allowed": True}`

Это нужно когда модель содержит SQLAlchemy объекты (Users):

```python
class LikeProcessResult(BaseModel):
    model_config = {"arbitrary_types_allowed": True}  # ⚠️ ОБЯЗАТЕЛЬНО!
    
    matched_user: Users | None  # Users - это SQLAlchemy модель
```

Без этой настройки Pydantic выдаст ошибку.

### 2. Типы `| None` для опциональных полей

```python
class LikeProcessResult(BaseModel):
    matched_user: Users | None  # Может быть None если не мэтч
    next_profile: Users | None  # Может быть None если анкеты закончились
```

Это современный синтаксис Python 3.10+ (вместо `Optional[Users]`).

### 3. Значения по умолчанию

```python
class MatchWithDetails(BaseModel):
    user: Users  # Обязательное поле
    match_date: datetime | None = None  # Опциональное с дефолтным значением
```

---

## 🎓 Сравнение: dict vs Pydantic

### Создание

```python
# dict
result = {
    "is_match": True,
    "matched_user": user,
    "next_profile": None
}

# Pydantic
result = LikeProcessResult(
    is_match=True,
    matched_user=user,
    current_user=current,  # Pydantic проверит что все обязательные поля заданы
    next_profile=None
)
```

### Доступ к данным

```python
# dict
if result["is_match"]:  # ❌ Нет автодополнения
    user = result["mathed_user"]  # ❌ Опечатка! KeyError в runtime

# Pydantic
if result.is_match:  # ✅ Автодополнение
    user = result.matched_user  # ✅ Опечатка подсветится в IDE
```

### Проверка типов

```python
# dict
result: dict = await service.process_like(...)
# Mypy не знает структуру dict

# Pydantic
result: LikeProcessResult = await service.process_like(...)
# Mypy знает все поля и их типы
```

---

## ✅ Чеклист

- [ ] Создал `LikeProcessResult` в `responses.py`
- [ ] Создал `DislikeProcessResult` в `responses.py`
- [ ] Создал `MatchWithDetails` в `responses.py`
- [ ] Добавил `model_config = {"arbitrary_types_allowed": True}` во все модели
- [ ] Изменил тип возврата `process_like()` на `LikeProcessResult`
- [ ] Изменил тип возврата `process_dislike()` на `DislikeProcessResult`
- [ ] Изменил тип возврата `get_user_matches_with_details()` на `list[MatchWithDetails]`
- [ ] Заменил `result["is_match"]` на `result.is_match` в Handler
- [ ] Заменил `result["next_profile"]` на `result.next_profile` в Handler
- [ ] Заменил `match_data["user"]` на `match_data.user` в Handler

---

**Готово! Теперь код типизирован и безопасен! 🎉**

