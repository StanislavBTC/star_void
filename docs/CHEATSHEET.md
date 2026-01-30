# Star_Void Cheat Sheet

Быстрая памятка для разработчиков.

---

## 🚀 Быстрый запуск

```bash
# Установка
pip install -r requirements.txt
pip install openai python-dotenv

# Конфигурация
cp env.example src/config/config.env
# Добавьте OPENAI_API_KEY в config.env

# Запуск
python mailn.py
```

---

## 📁 Структура (кратко)

```
star_void/
├── mailn.py              # Точка входа
├── src/
│   ├── ai/
│   │   ├── responder.py  # [TODO] Ядро ИИ
│   │   ├── filters.py    # [✓] Фильтры
│   │   └── silence.py    # [TODO] Молчание
│   ├── modules/          # [TODO] Режимы: ask, distort, void, silence
│   ├── utils/
│   │   ├── randomness.py # [✓] Промпты
│   │   ├── delay.py      # [TODO] Эффекты
│   │   └── text.py       # [TODO] Фрагменты
│   └── config/
│       ├── config.env    # API ключи
│       └── ai/*.txt      # [✓] Промпты ИИ
```

---

## 🎯 Основные функции

### responder.py
```python
respond(user_input: str, mode: str = "ask") -> Optional[str]
# Главная функция - генерирует ответ ИИ
```

### filters.py
```python
filter_advice(text: str) -> str        # Удаляет советы
filter_empathy(text: str) -> str       # Удаляет эмпатию
filter_length(text: str, max: int) -> str  # Обрезает
```

### silence.py
```python
should_be_silent(user_input: str, mode: str) -> bool
# True = молчать, False = говорить
```

### randomness.py
```python
random_prompt(name: str, **kwargs) -> str
# Загружает промпт из config/ai/{name}.txt
```

### delay.py
```python
random_delay(min_sec: float, max_sec: float) -> None
typing_effect(text: str, cps: int) -> None
```

### text.py
```python
extract_random_word(text: str) -> str
fragment_sentence(text: str) -> str
reduce_text(text: str, level: float) -> str
```

---

## 🎭 Режимы работы

| Режим     | Команда    | Что делает                    |
|-----------|------------|-------------------------------|
| ask       | `/ask`     | Диалог, краткие ответы        |
| distort   | `/distort` | Фрагментация, искажение       |
| void      | `/void`    | Пассивность, молчание         |
| silence   | `/silence` | Только молчание               |

---

## 🔄 Поток данных (кратко)

```
Пользователь → mailn.py → modules/{mode}.py → responder.py
                                                    ↓
                                        ┌───────────┴──────────┐
                                        ↓                      ↓
                                   silence.py             randomness.py
                                   (молчать?)             (промпты)
                                        ↓                      ↓
                                   если нет              LLM API
                                        ↓                      ↓
                                   filters.py ←───────────────┘
                                   (очистка)
                                        ↓
                            ← delay.py (пауза) ← typing_effect() ←
                                        ↓
                                    Вывод
```

---

## ⚙️ Конфигурация (config.env)

```env
# API
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai              # openai, anthropic, local
MODEL_NAME=gpt-3.5-turbo

# Поведение
SILENCE_PROBABILITY=0.2          # 0.0-1.0
MAX_TOKENS=150
TEMPERATURE=0.7

# Эффекты
MIN_DELAY_SEC=0.5
MAX_DELAY_SEC=2.0
TYPING_SPEED_CPS=30
```

---

## 🧩 Примеры кода

### Создать новый режим

```python
# src/modules/my_mode.py
from typing import Optional
from src.ai.responder import respond

def my_mode(user_input: str) -> Optional[str]:
    return respond(user_input, mode="my_mode")
```

```python
# mailn.py
from src.modules.my_mode import my_mode

modes = {
    "ask": ask,
    "my_mode": my_mode  # добавить
}
```

### Добавить фильтр

```python
# src/ai/filters.py
def filter_my_pattern(text: str) -> str:
    unwanted = ["паттерн1", "паттерн2"]
    for pattern in unwanted:
        text = text.replace(pattern, "")
    return text
```

```python
# src/ai/responder.py
from src.ai.filters import filter_my_pattern

filtered = filter_advice(raw)
filtered = filter_my_pattern(filtered)  # применить
```

### Вызвать LLM вручную

```python
from src.ai.responder import respond

# Базовый вызов
response = respond("Привет", mode="ask")
print(response)  # "А что тебе нужно?"

# Проверить молчание
from src.ai.silence import should_be_silent
if should_be_silent("...", "ask"):
    print("Молчание")
```

---

## 🐛 Отладка

### Проблема: ModuleNotFoundError
```bash
# Решение
pip install openai python-dotenv
```

### Проблема: No API key
```bash
# Проверить config.env
cat src/config/config.env | grep API_KEY
```

### Проблема: Импорты не работают
```bash
# Запускать из корня проекта
cd star_void
python mailn.py
```

### Проблема: Rate limit
```env
# Использовать GPT-3.5 (быстрее и дешевле)
MODEL_NAME=gpt-3.5-turbo
```

---

## 📊 Приоритеты разработки

### 🔴 Критично (блокирует все)
1. `responder.py` - интеграция с LLM
2. `silence.py` - логика молчания
3. Исправить `mailn.py` импорты

### 🟡 Важно (нужно для MVP)
4. `delay.py` - эффекты паузы
5. `text.py` - фрагментация
6. `ask.py`, `distort.py` - режимы

### 🟢 Желательно (улучшения)
7. Цветной вывод (rich)
8. Анимации загрузки
9. Тесты
10. Документация в коде

---

## 🧪 Тестирование

```bash
# Запустить все тесты
pytest tests/ -v

# Тест конкретного модуля
pytest tests/test_filters.py -v

# Тест с покрытием
pytest --cov=src tests/
```

### Быстрые тесты в REPL

```python
# Тест фильтров
from src.ai.filters import filter_advice
print(filter_advice("Попробуй сделать это"))  # ""

# Тест промптов
from src.utils.randomness import random_prompt
print(random_prompt("core"))  # промпт загружен

# Тест молчания
from src.ai.silence import should_be_silent
print(should_be_silent("...", "ask"))  # True/False
```

---

## 📝 Соглашения

### Именование
- Файлы: `lowercase_with_underscores.py`
- Функции: `lowercase_with_underscores()`
- Классы: `PascalCase`
- Константы: `UPPER_CASE`

### Возвращаемые значения
- Успех: `str` (текст ответа)
- Молчание: `None`
- Ошибка: `None` (с логированием)

### Docstrings
```python
def function(param: str) -> Optional[str]:
    """Краткое описание.
    
    Args:
        param: Описание параметра
        
    Returns:
        Описание возврата
    """
```

---

## 🔗 Полезные ссылки

- **Быстрый старт:** [QUICKSTART.md](QUICKSTART.md)
- **Дорожная карта:** [ROADMAP.md](ROADMAP.md)
- **Структура:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Спецификации:** [MODULE_SPECS.md](MODULE_SPECS.md)
- **Архитектура:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Индекс:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 💡 Команды mailn.py

```
/ask      - режим диалога
/distort  - режим искажения
/void     - режим пустоты
/silence  - режим молчания
/help     - справка
/quit     - выход
```

---

## 🎨 Философия кода

1. **Минимализм** - простой код
2. **Модульность** - одна функция = одна задача
3. **Недосказанность** - неполнота это нормально
4. **Тишина** - отсутствие тоже ответ
5. **Случайность** - рандом это фича

---

## ⏱️ Быстрые оценки

| Задача | Время |
|--------|-------|
| Настроить окружение | 15 мин |
| Реализовать responder.py | 2-3 ч |
| Реализовать silence.py | 1 ч |
| Реализовать delay.py | 1 ч |
| Реализовать text.py | 2 ч |
| Реализовать все режимы | 3 ч |
| Интеграция mailn.py | 1 ч |
| **ИТОГО MVP** | **10-12 ч** |

---

## 🎯 Следующий шаг

1. Открыть [QUICKSTART.md](QUICKSTART.md)
2. Дойти до Шага 3
3. Реализовать `responder.py`
4. Запустить первый тест
5. Продолжить по [ROADMAP.md](ROADMAP.md)

---

**Star_Void** - A terminal space where answers are optional