# 🔨 Гайд по рефакторингу для джуна

## 📋 Обзор задачи

Твоя задача — провести рефакторинг модуля `swipe` с использованием правильной архитектуры слоёв.

## 🎯 Цели рефакторинга

1. **Разделение ответственности** — каждый слой отвечает только за свою часть
2. **Устранение дублирования кода** — DRY принцип
3. **Улучшение тестируемости** — изолированные компоненты легче тестировать
4. **Чистая архитектура** — зависимости идут только в одну сторону

## 🏗️ Правильная архитектура слоёв

```
┌─────────────────────────────────────────┐
│           Handler (Controller)          │  ← Принимает события от Telegram
│  - Валидация входных данных             │  ← Управляет FSM состояниями
│  - Вызывает Service                     │  ← Координирует Service и Presenter
│  - Использует Presenter для UI          │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│              Service                     │  ← Бизнес-логика (БЕЗ UI!)
│  - Координирует DAO                     │  ← Проверка взаимных лайков
│  - Применяет бизнес-правила             │  ← Создание мэтчей
│  - Возвращает данные (не форматирует!)  │
└─────────────────┬───────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│                DAO                       │  ← Только работа с БД
│  - Запросы к БД через SQLAlchemy        │  ← Никакой бизнес-логики
│  - Создание/чтение/обновление записей   │  ← Управление сессиями
└─────────────────────────────────────────┘

        ┌─────────────────────────┐
        │  Presenter (View)       │  ← UI-логика (параллельно Handler)
        │  - Форматирование       │  ← Создание сообщений
        │  - Отправка в Telegram  │  ← Работа с клавиатурами
        └─────────────────────────┘
```

## 📝 Пошаговый план

### Шаг 0: Создать Pydantic модели для ответов Service

**ВАЖНО!** Service должен возвращать типизированные Pydantic модели, а не dict.

Создай модели в `src/bot/models/responses.py`:

```python
from pydantic import BaseModel
from src.bot.models.user import Users

class LikeProcessResult(BaseModel):
    """Результат обработки лайка"""
    model_config = {"arbitrary_types_allowed": True}
    
    is_match: bool
    matched_user: Users | None
    current_user: Users
    next_profile: Users | None

class DislikeProcessResult(BaseModel):
    """Результат обработки дизлайка"""
    model_config = {"arbitrary_types_allowed": True}
    
    next_profile: Users | None

class MatchWithDetails(BaseModel):
    """Мэтч с подробной информацией"""
    model_config = {"arbitrary_types_allowed": True}
    
    user: Users
    match_date: datetime | None = None
```

**Преимущества Pydantic моделей над dict:**

✅ **Автодополнение в IDE:**
- `result.is_match` вместо `result["is_match"]`
- IDE подсказывает доступные поля

✅ **Проверка типов:**
- Mypy/Pyright находят ошибки до запуска
- `result.is_match` гарантированно bool

✅ **Защита от опечаток:**
- `result.is_mach` → ошибка сразу
- `result["is_mach"]` → KeyError только в runtime

✅ **Документирование:**
- Структура данных явно описана в коде
- Легко понять что возвращает метод

---

### Шаг 1: Создать Presenter

Создай файл `src/bot/presenters/swipe.py`:

```python
from aiogram.types import Message, CallbackQuery
from src.bot.models.user import Users
from src.bot.keyboards.swipe import get_swipe_keyboard

class SwipePresenter:
    """Отвечает за форматирование и отправку UI"""
    
    @staticmethod
    def format_profile(user: Users, hide_name: bool = False) -> str:
        """Форматирование анкеты для отображения"""
        if hide_name:
            return f"🎭 Кто-то, {user.age}, {user.city}\n{user.interests}"
        return f"{user.name}, {user.age}, {user.city}\n{user.interests}"
    
    @staticmethod
    async def send_profile(
        target: Message | CallbackQuery, 
        profile: Users, 
        hide_name: bool = False,
        state_context = None
    ):
        """Отправка анкеты пользователю"""
        profile_text = SwipePresenter.format_profile(profile, hide_name)
        keyboard = get_swipe_keyboard(profile.tg_id)
        
        # Определяем куда отправлять
        if isinstance(target, CallbackQuery):
            message = target.message
        else:
            message = target
            
        # Отправляем с фото или без
        if profile.photo_id:
            await message.answer_photo(
                photo=profile.photo_id,
                caption=profile_text,
                reply_markup=keyboard
            )
        else:
            await message.answer(profile_text, reply_markup=keyboard)
    
    @staticmethod
    def format_match_message(matched_user: Users) -> str:
        """Форматирование сообщения о мэтче"""
        username = f"@{matched_user.username}" if matched_user.username else "без username"
        return (
            f"🔥 Взаимная симпатия!\n\n"
            f"Вы понравились друг другу!\n"
            f"Контакт: {username}\n\n"
            f"Можете начать общение! 💬"
        )
    
    @staticmethod
    def format_like_notification() -> str:
        """Сообщение 'Ты кому-то понравился'"""
        return "❤️ Ты кому-то понравился!\n\nПоказать кто это?"
    
    @staticmethod
    async def send_no_profiles_message(target: Message | CallbackQuery):
        """Сообщение когда анкеты закончились"""
        text = "😔 К сожалению, подходящих анкет пока нет. Попробуй позже!"
        if isinstance(target, CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
```

### Шаг 2: Расширить DAO

Добавь методы в `src/bot/dao/user.py`:

```python
async def get_next_profile(
    self, 
    user_id: int, 
    excluded_ids: list[int], 
    gender_filter: Gender | None
) -> Optional[Users]:
    """Получить следующую анкету с фильтрами"""
    # Переместить логику из SwipeService.get_next_profile
    pass

async def get_profiles_by_ids(self, user_ids: list[int]) -> list[Users]:
    """Получить несколько профилей по ID"""
    pass
```

Добавь в `src/bot/dao/like.py`:

```python
async def get_rated_user_ids(self, user_id: int) -> list[int]:
    """Получить ID всех оценённых пользователей"""
    pass

async def get_users_who_liked_me(self, user_id: int) -> list[int]:
    """Получить ID тех, кто лайкнул меня"""
    pass

async def get_unrated_from_list(
    self, 
    user_id: int, 
    candidate_ids: list[int]
) -> list[int]:
    """Из списка кандидатов вернуть тех, кого ещё не оценил"""
    pass
```

### Шаг 3: Очистить Service

Переделай `src/bot/services/swipe.py`:

```python
from src.bot.models.responses import LikeProcessResult, DislikeProcessResult, MatchWithDetails

class SwipeService:
    """Чистая бизнес-логика без UI"""
    
    async def get_next_profile(self, user_id: int) -> Optional[Users]:
        """Получить следующую анкету"""
        # 1. Получить текущего пользователя
        current_user = await self.users_dao.get_by_tg_id(user_id)
        if not current_user:
            return None
            
        # 2. Получить уже оценённых
        rated_ids = await self.likes_dao.get_rated_user_ids(user_id)
        
        # 3. Получить анкету с учётом фильтров
        return await self.users_dao.get_next_profile(
            user_id=user_id,
            excluded_ids=rated_ids,
            gender_filter=current_user.gender_interest
        )
    
    async def get_profiles_who_liked_me(self, user_id: int) -> list[Users]:
        """Получить анкеты тех, кто лайкнул меня"""
        # 1. Кто лайкнул
        liked_me_ids = await self.likes_dao.get_users_who_liked_me(user_id)
        if not liked_me_ids:
            return []
            
        # 2. Кого я ещё не оценил
        not_rated = await self.likes_dao.get_unrated_from_list(
            user_id, liked_me_ids
        )
        if not not_rated:
            return []
            
        # 3. Получить профили
        return await self.users_dao.get_profiles_by_ids(not_rated)
    
    async def process_like(
        self, 
        from_user_id: int, 
        to_user_id: int
    ) -> LikeProcessResult:  # ✅ Pydantic модель вместо dict!
        """
        Обработать лайк БЕЗ отправки уведомлений
        
        Returns:
            LikeProcessResult с полями:
            - is_match: bool
            - matched_user: Users | None
            - current_user: Users
            - next_profile: Users | None
        """
        # Добавляем лайк
        await self.likes_dao.add_like(from_user_id, to_user_id, is_like=True)
        
        # Проверяем взаимность
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
    ) -> DislikeProcessResult:  # ✅ Pydantic модель
        """Обработать дизлайк"""
        await self.likes_dao.add_like(from_user_id, to_user_id, is_like=False)
        next_profile = await self.get_next_profile(from_user_id)
        
        return DislikeProcessResult(next_profile=next_profile)
    
    async def get_user_matches_with_details(
        self, 
        user_id: int
    ) -> list[MatchWithDetails]:  # ✅ Pydantic модель
        """Получить мэтчи с данными пользователей"""
        matches = await self.matches_dao.get_user_matches(user_id)
        result = []
        
        for match in matches:
            other_id = match.user2_id if match.user1_id == user_id else match.user1_id
            other_user = await self.users_dao.get_by_tg_id(other_id)
            if other_user:
                result.append(
                    MatchWithDetails(
                        user=other_user,
                        match_date=match.created_at
                    )
                )
        
        return result
```

### Шаг 4: Упростить Handler

Переделай `src/bot/handlers/swipe.py`:

```python
from src.bot.presenters.swipe import SwipePresenter

@swipe_router.message(Command("search"))
async def start_search(
    message: Message, 
    swipe_service: SwipeService,
    presenter: SwipePresenter,
    state: FSMContext
):
    """Начать просмотр анкет"""
    user_id = message.from_user.id
    next_profile = await swipe_service.get_next_profile(user_id)
    
    if not next_profile:
        await presenter.send_no_profiles_message(message)
        return
    
    await state.set_state(SwipeStates.normal_browsing)
    await presenter.send_profile(message, next_profile)


@swipe_router.callback_query(F.data.startswith("like_"))
async def process_like_callback(
    callback: CallbackQuery,
    swipe_service: SwipeService,
    presenter: SwipePresenter,
    state: FSMContext,
    bot: Bot
):
    """Обработка лайка"""
    to_user_id = int(callback.data.split("_")[1])
    from_user_id = callback.from_user.id
    
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Получаем состояние
    current_state = await state.get_state()
    
    # Обрабатываем лайк (БЕЗ отправки уведомлений)
    result = await swipe_service.process_like(from_user_id, to_user_id)
    
    # ✅ Используем Pydantic модель - автодополнение работает!
    # result.is_match вместо result["is_match"]
    if result.is_match:
        match_text = presenter.format_match_message(result.matched_user)
        await callback.message.answer(match_text)
        
        # Уведомляем второго пользователя
        await bot.send_message(
            to_user_id,
            presenter.format_match_message(result.current_user)
        )
    else:
        # Уведомление о лайке
        from src.bot.keyboards.swipe import get_show_likes_keyboard
        await bot.send_message(
            to_user_id,
            presenter.format_like_notification(),
            reply_markup=get_show_likes_keyboard()
        )
    
    # Определяем следующую анкету
    if current_state == SwipeStates.viewing_likes:
        profiles = await swipe_service.get_profiles_who_liked_me(from_user_id)
        next_profile = profiles[0] if profiles else result.next_profile  # ✅ .next_profile
        hide_name = bool(profiles)
    else:
        next_profile = result.next_profile  # ✅ .next_profile
        hide_name = False
    
    if not next_profile:
        await callback.message.answer("😔 Анкеты закончились!")
        await state.clear()
        await callback.answer()
        return
    
    # Отправляем следующую анкету
    await presenter.send_profile(callback, next_profile, hide_name)
    await callback.answer("❤️ Лайк отправлен!")


@swipe_router.message(Command("matches"))
async def show_matches(
    message: Message,
    swipe_service: SwipeService,
    presenter: SwipePresenter
):
    """Показать мэтчи"""
    user_id = message.from_user.id
    matches = await swipe_service.get_user_matches_with_details(user_id)
    
    if not matches:
        await message.answer("У тебя пока нет мэтчей 😔")
        return
    
    # ✅ Форматирование в Presenter + используем Pydantic модели
    matches_text = "💕 Твои мэтчи:\n\n"
    for match_data in matches:  # match_data это MatchWithDetails
        user = match_data.user  # ✅ .user вместо ["user"]
        username = f"@{user.username}" if user.username else "без username"
        matches_text += f"• {user.name} - {username}\n"
    
    await message.answer(matches_text)
```

## ✅ Чеклист перед завершением

- [ ] Создан файл `src/bot/presenters/swipe.py` с классом `SwipePresenter`
- [ ] Добавлены методы в DAO для работы с БД
- [ ] Из `SwipeService` удалён импорт `get_show_likes_keyboard`
- [ ] Из `SwipeService` удалён метод `format_profile`
- [ ] Из `SwipeService.process_like` удалён параметр `bot`
- [ ] Из `SwipeService` удалены все `bot.send_message()`
- [ ] Из Handler удалены прямые обращения к DAO (`matches_dao`, `users_dao`)
- [ ] Устранено дублирование кода отправки анкет
- [ ] Все тесты проходят (если есть)
- [ ] Код проверен линтером

## 🎓 Что ты изучишь

1. **SOLID принципы** — Single Responsibility, Dependency Inversion
2. **Layered Architecture** — правильное разделение на слои
3. **Separation of Concerns** — разделение ответственности
4. **DRY** — Don't Repeat Yourself
5. **Clean Code** — читаемый и поддерживаемый код

## 📚 Полезные ссылки

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual-articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [MVC/MVP/MVVM patterns](https://medium.com/@ankit.sinhal/mvc-mvp-and-mvvm-design-pattern-6e169567bbad)

---

**Удачи! 🚀 Если возникнут вопросы — изучай TODO-комментарии в коде!**

