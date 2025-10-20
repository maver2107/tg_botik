# tg_bot project

## 🔨 Задача для джуна: Рефакторинг архитектуры

В проекте есть проблемы с архитектурой — нарушение разделения ответственности между слоями.

### 📍 Где смотреть:

1. **Файлы с TODO-комментариями:**
   - `src/bot/handlers/swipe.py` — 6 проблем с архитектурой
   - `src/bot/services/swipe.py` — проблемы с UI в бизнес-логике

2. **Обучающие материалы:**
   - `TODO_FOR_JUNIOR.md` — краткий чек-лист всех задач ⭐ **НАЧНИ С ЭТОГО**
   - `ARCHITECTURE_PROBLEMS.md` — визуальное объяснение проблем
   - `REFACTORING_GUIDE.md` — полный гайд с примерами кода
   - `PYDANTIC_MODELS_EXAMPLE.md` — зачем нужны Pydantic модели вместо dict

### 🎯 Твоя задача:

Провести рефакторинг модуля `swipe` с правильным разделением слоёв:
- Handler → Service → DAO
- Handler → Presenter (для UI)

**Удачи! 🚀**

---

## Описание проекта

Telegram бот для знакомств (dating bot) с функционалом свайпов, лайков и мэтчей.

### Технологии:
- Python 3.13+
- aiogram 3.22+ (Telegram Bot Framework)
- SQLAlchemy 2.0+ (ORM)
- PostgreSQL + asyncpg
- Alembic (миграции БД)
