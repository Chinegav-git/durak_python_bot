# Управління Callback запитами в Telegram боті

## Проблема накопичення callback'ів

Telegram має обмеження на обробку callback запитів:
- **Таймаут:** Callback повинен бути оброблений протягом 30 секунд
- **Обмеження:** Багато невідповідей можуть призвести до блокування
- **Дублювання:** Повторні натискання на ті самі кнопки

## Рішення

### 1. CallbackManager
Клас `CallbackManager` забезпечує:
- ✅ Контроль одночасних callback'ів (максимум 10)
- ✅ Запобігання дублюванню (5 хвилин)
- ✅ Автоматичне очищення старих записів
- ✅ Безпечна відповідь на callback

### 2. Декоратори

#### `safe_callback_handler`
```python
from durak.utils.callback_decorator import safe_callback_handler

@router.callback_query(GameCallback.filter(F.action == "join"))
@safe_callback_handler(show_error=True, timeout=30)
async def join_callback_handler(call: types.CallbackQuery, callback_data: GameCallback, gm: GameManager):
    # Ваш код обробки
    pass
```

#### `auto_callback_answer`
```python
from durak.utils.callback_decorator import auto_callback_answer

@router.callback_query(GameCallback.filter(F.action == "settings"))
@auto_callback_answer("⚙️ Налаштування відкрито")
async def settings_callback_handler(call: types.CallbackQuery):
    # Ваш код обробки
    pass
```

## Моніторинг

### Логування
- `INFO`: Очищення старих callback'ів
- `WARNING`: Дублікати та перевищення лімітів
- `ERROR`: Помилки обробки

### Статистика
```python
from durak.utils import callback_manager

# Кількість очікуючих callback'ів
pending = len(callback_manager.pending_callbacks)

# Кількість оброблених callback'ів
processed = len(callback_manager.processed_callbacks)
```

## Найкращі практики

### 1. Швидка обробка
```python
# ❌ Погано - довга обробка
@router.callback_query(...)
async def slow_handler(call):
    await long_database_operation()  # > 30 секунд
    await call.answer("Готово")

# ✅ Добре - швидка відповідь
@router.callback_query(...)
@safe_callback_handler()
async def fast_handler(call):
    asyncio.create_task(long_database_operation())  # Фонова задача
    await call.answer("Обробка розпочата...")
```

### 2. Обробка помилок
```python
@router.callback_query(...)
@safe_callback_handler()
async def safe_handler(call):
    try:
        # Ризикована операція
        result = await risky_operation()
        await call.answer(f"✅ {result}")
    except SpecificError as e:
        await call.answer(f"⚠️ {e}", show_alert=True)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await call.answer("❌ Внутрішня помилка", show_alert=True)
```

### 3. Валідація даних
```python
@router.callback_query(...)
@safe_callback_handler()
async def validated_handler(call, callback_data: GameCallback):
    # Перевірка валідності даних
    if not callback_data.game_id:
        await call.answer("❌ Невідома гра", show_alert=True)
        return
    
    # Перевірка прав доступу
    if not await has_permission(call.from_user.id, callback_data.game_id):
        await call.answer("❌ Немає доступу", show_alert=True)
        return
    
    # Основна логіка
    await process_game_action(call, callback_data)
```

## Налаштування

### Параметри CallbackManager
```python
callback_manager.callback_timeout = 30  # Таймаут обробки
callback_manager.max_concurrent_callbacks = 10  # Максимальна кількість
```

### Періодичне очищення
```python
# У bot.py вже налаштовано
async def periodic_callback_cleanup():
    while True:
        callback_manager.cleanup_old_callbacks()
        await asyncio.sleep(60)  # Кожну хвилину
```

## Діагностика проблем

### 1. Перевірка статусу
```python
print(f"Pending callbacks: {len(callback_manager.pending_callbacks)}")
print(f"Processed callbacks: {len(callback_manager.processed_callbacks)}")
```

### 2. Логування
```bash
# Увімкнути логування
export LOGLEVEL=INFO
python bot.py
```

### 3. Моніторинг Telegram
- Використовуйте `@BotFather` для перевірки статусу бота
- Моніторте `rate limits` в Telegram API

## Важливо!

1. **Ніколи не блокуйте** callback обробник довго (> 30 секунд)
2. **Завжди відповідайте** на callback, навіть якщо сталася помилка
3. **Використовуйте фонові задачі** для довгих операцій
4. **Валідуйте дані** перед обробкою
5. **Логуйте помилки** для діагностики
