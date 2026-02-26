# Multilingual Localization Guide / Багатомовна локалізація

## Overview / Огляд

This bot now supports multilingual localization with automatic language detection and user preference management. The system currently supports three languages:
- Ukrainian (uk) - default
- Russian (ru) 
- English (en)

Цей бот тепер підтримує багатомовну локалізацію з автоматичним виявленням мови та управлінням мовними налаштуваннями. Система наразі підтримує три мови:
- Українська (uk) - за замовчуванням
- Російська (ru)
- Англійська (en)

## How it works / Як це працює

### 1. Language Detection / Виявлення мови

The system automatically detects user language in this order:
1. **User Preference**: Checks if user has set a language preference in the database
2. **Telegram Profile**: Falls back to user's Telegram language code
3. **Default**: Defaults to Ukrainian if neither is available

Система автоматично виявляє мову користувача в такому порядку:
1. **Налаштування користувача**: Перевіряє, чи встановив користувач мову в базі даних
2. **Профіль Telegram**: Повертається до мовного коду користувача в Telegram
3. **За замовчуванням**: Використовує українську, якщо нічого не доступно

### 2. Translation Files / Файли перекладів

Translation files are stored in `durak/locales/` as JSON files:
- `uk.json` - Ukrainian translations
- `ru.json` - Russian translations  
- `en.json` - English translations

Файли перекладів зберігаються в `durak/locales/` як JSON файли:
- `uk.json` - українські переклади
- `ru.json` - російські переклади
- `en.json` - англійські переклади

### 3. Using Translations / Використання перекладів

In handlers, use the `t()` function:

```python
from durak.utils.i18n import t

# Simple translation
await message.answer(t('game.no_game'))

# With variables
await message.answer(t('game.joined', name=user.first_name))
```

В обробниках використовуйте функцію `t()`:

```python
from durak.utils.i18n import t

# Простий переклад
await message.answer(t('game.no_game'))

# зі змінними
await message.answer(t('game.joined', name=user.first_name))
```

## Translation Keys / Ключі перекладів

Translation keys use dot notation for organization:
- `game.created` - Game created message
- `buttons.join` - Join button text
- `commands.new` - New command description
- `errors.unexpected` - Unexpected error message

Ключі перекладів використовують нотацію з крапками для організації:
- `game.created` - повідомлення про створення гри
- `buttons.join` - текст кнопки приєднатися
- `commands.new` - опис команди нової гри
- `errors.unexpected` - повідомлення про несподівану помилку

## Language Selection / Вибір мови

Users can change their language preference through:
1. **Settings Menu**: Use `/settings` command and select "🌐 Мова"
2. **Automatic Detection**: Language is automatically detected from Telegram profile

Користувачі можуть змінити свої мовні налаштування через:
1. **Меню налаштувань**: Використовуйте команду `/settings` і оберіть "🌐 Мова"
2. **Автоматичне виявлення**: Мова автоматично виявляється з профілю Telegram

## Adding New Translations / Додавання нових перекладів

### 1. Add to Translation Files / Додати до файлів перекладів

Add the same key to all three language files:

**uk.json:**
```json
{
  "new_key": "Новий переклад"
}
```

**ru.json:**
```json
{
  "new_key": "Новый перевод"
}
```

**en.json:**
```json
{
  "new_key": "New translation"
}
```

### 2. Use in Code / Використати в коді

```python
from durak.utils.i18n import t
await message.answer(t('new_key'))
```

## Database Migration / Міграція бази даних

The system adds a `language` field to the `UserSetting` model. Run the migration:

Система додає поле `language` до моделі `UserSetting`. Запустіть міграцію:

```bash
aerich migrate
aerich upgrade
```

## Supported Languages / Підтримувані мови

| Code | Language | Native Name |
|------|----------|-------------|
| uk   | Ukrainian | Українська |
| ru   | Russian   | Русский    |
| en   | English   | English    |

To add a new language:
1. Create new JSON file in `durak/locales/`
2. Add language to `i18n.get_available_languages()`
3. Update language detection logic

Щоб додати нову мову:
1. Створіть новий JSON файл в `durak/locales/`
2. Додайте мову до `i18n.get_available_languages()`
3. Оновіть логіку виявлення мови

## Best Practices / Найкращі практики

1. **Use descriptive keys**: Use keys like `game.player_joined` instead of `msg1`
2. **Keep consistent**: Use the same keys across all language files
3. **Test all languages**: Verify translations work in all supported languages
4. **Use variables**: For dynamic content, use `{variable}` syntax in translations

1. **Використовуйте описові ключі**: Використовуйте ключі на кшталт `game.player_joined` замість `msg1`
2. **Зберігайте узгодженість**: Використовуйте однакові ключі у всіх файлах мов
3. **Тестуйте всі мови**: Перевіряйте, що переклади працюють у всіх підтримуваних мовах
4. **Використовуйте змінні**: Для динамічного контенту використовуйте синтаксис `{variable}` в перекладах
