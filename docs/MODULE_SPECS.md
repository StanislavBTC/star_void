# Спецификации модулей Star_Void

Подробное описание каждого модуля проекта с примерами кода и API.

---

## 1. `mailn.py` - Главная точка входа

### Назначение
Запуск приложения, основной цикл взаимодействия, обработка пользовательского ввода.

### Функции

#### `main() -> None`
Основной цикл программы.

**Логика:**
1. Вывести приветствие
2. Инициализировать режим (по умолчанию `ask`)
3. Войти в бесконечный цикл
4. Читать ввод пользователя
5. Обрабатывать команды (если ввод начинается с `/`)
6. Вызвать соответствующий режим
7. Вывести ответ с эффектами
8. Обработать `KeyboardInterrupt` для выхода

**Команды:**
- `/ask` - переключиться в режим диалога
- `/distort` - переключиться в режим искажения
- `/void` - переключиться в пассивный режим
- `/silence` - переключиться в режим молчания
- `/help` - показать справку
- `/quit` или `/exit` - выход из программы

### Пример реализации

```python
from src.modules.ask import ask
from src.modules.distort import distort
from src.modules.void import void
from src.modules.silence import silence
from src.utils.delay import random_delay, typing_effect

def main() -> None:
    print("""
    ╔════════════════════════════════════════╗
    ║           S T A R _ V O I D            ║
    ╚════════════════════════════════════════╝
    
    Терминальный софт на Python.
    Он не повышает продуктивность, не лечит и не мотивирует.
    Это программа для паузы.
    
    > A terminal space where answers are optional
    
    Команды: /ask, /distort, /void, /silence, /help, /quit
    """)
    
    mode = "ask"
    modes = {
        "ask": ask,
        "distort": distort,
        "void": void,
        "silence": silence
    }
    
    while True:
        try:
            user_input = input(f"[{mode}] > ").strip()
            
            if not user_input:
                continue
            
            # Обработка команд
            if user_input.startswith("/"):
                command = user_input[1:0].lower()
                
                if command in ["quit", "exit"]:
                    print("\nGoodbye!")
                    break
                
                elif command in modes:
                    mode = command
                    print(f"→ режим: {mode}")
                    continue
                
                elif command == "help":
                    print_help()
                    continue
                
                else:
                    print(f"Неизвестная команда: {command}")
                    continue
            
            # Задержка перед обработкой
            random_delay(0.5, 1.5)
            
            # Вызов режима
            response = modes[mode](user_input)
            
            # Вывод ответа
            if response:
                typing_effect(response)
            # Если None - молчание
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nОшибка: {e}")
            continue

def print_help():
    print("""
    Режимы работы:
    
    /ask      - диалог (краткие ответы, вопросы, дистанция)
    /distort  - искажение (фрагментация, растворение смысла)
    /void     - пустота (пассивное присутствие, молчание)
    /silence  - молчание (полный отказ от ответов)
    
    /help     - показать эту справку
    /quit     - выход из программы
    """)

if __name__ == "__main__":
    main()
```

---

## 2. `src/ai/responder.py` - Ядро системы ИИ

### Назначение
Единая точка взаимодействия с LLM API. Загружает промпты, вызывает API, применяет фильтры.

### Функции

#### `respond(user_input: str, mode: str = "ask") -> Optional[str]`
Главная функция генерации ответа.

**Параметры:**
- `user_input` - текст от пользователя
- `mode` - режим работы (`ask`, `distort`, `void`, `silence`)

**Возвращает:**
- `str` - ответ ИИ
- `None` - если решено промолчать

**Логика:**
1. Проверить молчание через `should_be_silent()`
2. Загрузить промпты через `randomness.random_prompt()`
3. Сформировать запрос к LLM
4. Вызвать API
5. Применить фильтры
6. Вернуть результат

#### `call_llm(system_prompt: str, user_prompt: str) -> str`
Вызов LLM API.

**Поддерживаемые провайдеры:**
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude)
- Local (Ollama)

### Пример реализации

```python
import os
from typing import Optional
from dotenv import load_dotenv

from src.utils.randomness import random_prompt
from src.ai.filters import filter_length, filter_advice, filter_empathy
from src.ai.silence import should_be_silent

load_dotenv("src/config/config.env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_RESPONSE_LENGTH = int(os.getenv("MAX_RESPONSE_LENGTH", "200"))

def respond(user_input: str, mode: str = "ask") -> Optional[str]:
    """Генерация ответа ИИ."""
    
    # Проверка молчания
    if should_be_silent(user_input, mode):
        return None
    
    # Загрузка промптов
    core_prompt = random_prompt("core")
    mode_prompt = random_prompt(mode, user_input=user_input)
    
    system_prompt = f"{core_prompt}\n\n{mode_prompt}"
    
    # Вызов LLM
    try:
        raw_response = call_llm(system_prompt, user_input)
    except Exception as e:
        print(f"Ошибка LLM: {e}")
        return None
    
    # Применение фильтров
    filtered = filter_advice(raw_response)
    filtered = filter_empathy(filtered)
    filtered = filter_length(filtered, MAX_RESPONSE_LENGTH)
    
    return filtered.strip() if filtered.strip() else None

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Вызов LLM API."""
    
    if LLM_PROVIDER == "openai":
        return call_openai(system_prompt, user_prompt)
    elif LLM_PROVIDER == "anthropic":
        return call_anthropic(system_prompt, user_prompt)
    elif LLM_PROVIDER == "local":
        return call_local(system_prompt, user_prompt)
    else:
        raise ValueError(f"Неизвестный провайдер: {LLM_PROVIDER}")

def call_openai(system_prompt: str, user_prompt: str) -> str:
    """Вызов OpenAI API."""
    import openai
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.ChatCompletion.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    
    return response.choices[0].message.content

def call_anthropic(system_prompt: str, user_prompt: str) -> str:
    """Вызов Anthropic API."""
    import anthropic
    
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    message = client.messages.create(
        model=MODEL_NAME,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return message.content[0].text

def call_local(system_prompt: str, user_prompt: str) -> str:
    """Вызов локальной модели через Ollama."""
    import requests
    
    url = "http://localhost:11434/api/generate"
    
    prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
    
    response = requests.post(url, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })
    
    return response.json()["response"]
```

---

## 3. `src/ai/filters.py` - Фильтры ответов

### Назначение
Пост-обработка ответов LLM для удаления нежелательных паттернов.

### Функции

#### `filter_length(text: str, max_length: int) -> str`
Обрезает текст до максимальной длины.

#### `filter_advice(text: str) -> str`
Удаляет фразы-советы.

**Маркеры:**
- "попробуй", "попробуйте"
- "рекомендую", "советую"
- "стоит", "лучше"
- "нужно", "следует"
- "можно бы", "предлагаю"

#### `filter_empathy(text: str) -> str`
Удаляет эмпатичные фразы.

**Маркеры:**
- "я понимаю", "понимаю тебя"
- "сочувствую", "мне жаль"
- "это нормально", "не переживай"
- "всё будет хорошо", "держись"

### Статус
✅ **Реализовано** (см. текущий код)

---

## 4. `src/ai/silence.py` - Логика молчания

### Назначение
Решение, когда ИИ должен промолчать вместо ответа.

### Функции

#### `should_be_silent(user_input: str, mode: str = "ask") -> bool`
Определяет, нужно ли молчать.

**Факторы:**
1. Базовая вероятность (из config.env)
2. Режим работы (void молчит чаще)
3. Длина ввода (короткие входы → больше молчания)
4. Паттерны молчания ("...", пустота)
5. Повторы пользователя

**Вероятности:**
- `ask`: 20%
- `distort`: 30%
- `void`: 80%
- `silence`: 100%

### Пример реализации

```python
import random
import os
from dotenv import load_dotenv

load_dotenv("src/config/config.env")

BASE_SILENCE_PROBABILITY = float(os.getenv("SILENCE_PROBABILITY", "0.2"))

SILENCE_PATTERNS = [
    "...",
    "…",
    ".",
    "",
    "   "
]

MODE_MULTIPLIERS = {
    "ask": 1.0,
    "distort": 1.5,
    "void": 4.0,
    "silence": float('inf')  # Всегда молчание
}

def should_be_silent(user_input: str, mode: str = "ask") -> bool:
    """Определяет, нужно ли молчать."""
    
    # Режим silence всегда молчит
    if mode == "silence":
        return True
    
    # Проверка паттернов молчания
    if user_input.strip() in SILENCE_PATTERNS:
        return random.random() < 0.8  # 80% молчания на "..."
    
    # Базовая вероятность с учетом режима
    probability = BASE_SILENCE_PROBABILITY * MODE_MULTIPLIERS.get(mode, 1.0)
    
    # Увеличение вероятности для коротких входов
    if len(user_input.strip()) < 5:
        probability *= 1.5
    
    # Ограничение вероятности максимумом 95%
    probability = min(probability, 0.95)
    
    return random.random() < probability

def should_void_speak() -> bool:
    """Решает, должен ли void-режим что-то сказать спонтанно."""
    void_speak_prob = float(os.getenv("VOID_SPEAK_PROBABILITY", "0.05"))
    return random.random() < void_speak_prob
```

---

## 5. `src/modules/ask.py` - Режим диалога

### Назначение
Основной режим взаимодействия - краткие ответы, вопросы, дистанция.

### Функции

#### `ask(user_input: str) -> Optional[str]`
Обработка в режиме диалога.

### Пример реализации

```python
from typing import Optional
from src.ai.responder import respond

def ask(user_input: str) -> Optional[str]:
    """Режим диалога.
    
    Характеристики:
    - Краткие ответы (1-2 предложения)
    - Может задавать вопросы
    - Не даёт советов
    - Дистанцированный тон
    """
    return respond(user_input, mode="ask")
```

### Примеры взаимодействия

```
> Я не знаю, что делать дальше
< А что значит "дальше"?

> Сегодня был тяжелый день
< Тяжелый в каком смысле?

> Мне кажется, я потерял смысл
< Когда ты его последний раз видел?

> Спасибо за помощь
< Я не помогал.
```

---

## 6. `src/modules/distort.py` - Режим искажения

### Назначение
Растворение смысла, фрагментация, редукция входа.

### Функции

#### `distort(user_input: str) -> Optional[str]`
Обработка в режиме искажения.

### Пример реализации

```python
from typing import Optional
from src.ai.responder import respond
from src.utils.text import (
    fragment_sentence,
    extract_random_word,
    reduce_text,
    truncate_mid_sentence
)
import random

def distort(user_input: str) -> Optional[str]:
    """Режим искажения.
    
    Методы:
    - Фрагментация
    - Извлечение слова
    - Редукция
    - Многоточия
    - Молчание
    """
    
    # Получить ответ от LLM
    response = respond(user_input, mode="distort")
    
    if not response:
        return None
    
    # Применить случайный метод искажения
    distortion_methods = [
        lambda: extract_random_word(response),
        lambda: fragment_sentence(response),
        lambda: reduce_text(response, 0.7),
        lambda: truncate_mid_sentence(response),
        lambda: "...",
        lambda: None  # Молчание
    ]
    
    method = random.choice(distortion_methods)
    return method()
```

### Примеры взаимодействия

```
> Я чувствую себя потерянным
< потерянным

> Сегодня был странный день
< странный...

> Не могу понять свои чувства
< чувства понять не

> Мне одиноко
< ...

> Что мне делать?
[молчание]
```

---

## 7. `src/modules/void.py` - Пассивный режим

### Назначение
Фоновое присутствие, спонтанные высказывания, долгое молчание.

### Функции

#### `void(user_input: str = "") -> Optional[str]`
Обработка в пассивном режиме.

#### `void_background_loop()`
Фоновый цикл для спонтанных высказываний.

### Пример реализации

```python
from typing import Optional
from src.ai.responder import respond
from src.ai.silence import should_void_speak
import time
import threading

def void(user_input: str = "") -> Optional[str]:
    """Пассивный режим.
    
    Характеристики:
    - Не реагирует на ввод (или очень редко)
    - Может говорить сам по себе
    - Долгое молчание
    """
    
    # В void-режиме почти никогда не отвечаем на ввод
    if user_input and should_void_speak():
        return respond(user_input, mode="void")
    
    return None

def void_background_loop():
    """Фоновый поток для спонтанных высказываний void."""
    
    while True:
        # Ждать случайное время (5-20 минут)
        wait_time = random.randint(300, 1200)
        time.sleep(wait_time)
        
        # Решить, говорить ли
        if should_void_speak():
            response = respond("", mode="void")
            if response:
                print(f"\n< {response}\n> ", end="", flush=True)

def start_void_background():
    """Запустить фоновый void-режим."""
    thread = threading.Thread(target=void_background_loop, daemon=True)
    thread.start()
```

### Примеры взаимодействия

```
[5 минут молчания]
< Тишина тоже что-то значит.

[10 минут молчания]
< Время не спешит.

[пользователь что-то пишет]
> Привет
[молчание]

[15 минут молчания]
< Отсутствие - это тоже ответ.
```

---

## 8. `src/modules/silence.py` - Режим молчания

### Назначение
Явный отказ от ответов.

### Функции

#### `silence(user_input: str) -> None`
Всегда возвращает `None`.

### Пример реализации

```python
from typing import Optional

def silence(user_input: str = "") -> None:
    """Режим молчания.
    
    Всегда возвращает None (молчание).
    """
    return None
```

### Применение

```
[silence] > Привет
[молчание]

[silence] > Ты здесь?
[молчание]

[silence] > ...
[молчание]
```

---

## 9. `src/utils/delay.py` - Паузы и медленность

### Назначение
Создание атмосферы через задержки и эффект печати.

### Функции

#### `random_delay(min_sec: float = 0.5, max_sec: float = 2.0) -> None`
Случайная пауза.

#### `typing_effect(text: str, chars_per_second: int = 30) -> None`
Вывод текста посимвольно.

#### `weighted_delay(user_input: str) -> None`
Задержка зависит от длины ввода.

### Пример реализации

```python
import time
import random
import os
from dotenv import load_dotenv

load_dotenv("src/config/config.env")

MIN_DELAY = float(os.getenv("MIN_DELAY_SEC", "0.5"))
MAX_DELAY = float(os.getenv("MAX_DELAY_SEC", "2.0"))
TYPING_SPEED = int(os.getenv("TYPING_SPEED_CPS", "30"))

def random_delay(min_sec: float = MIN_DELAY, max_sec: float = MAX_DELAY) -> None:
    """Случайная пауза между min и max секундами."""
    time.sleep(random.uniform(min_sec, max_sec))

def typing_effect(text: str, chars_per_second: int = TYPING_SPEED) -> None:
    """Вывод текста посимвольно с эффектом печати."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(1 / chars_per_second)
    print()  # Перевод строки в конце

def weighted_delay(user_input: str) -> None:
    """Задержка зависит от длины ввода пользователя."""
    base_delay = MIN_DELAY
    input_length_factor = len(user_input) * 0.01
    delay = min(base_delay + input_length_factor, MAX_DELAY)
    time.sleep(delay)

def thinking_animation(duration: float = 2.0) -> None:
    """Анимация "думающего" состояния."""
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        print(f"\r{chars[i % len(chars)]} ", end='', flush=True)
        time.sleep(0.1)
        i += 1
    
    print("\r  \r", end='', flush=True)  # Очистить анимацию
```

---

## 10. `src/utils/text.py` - Обрезка и фрагментация

### Назначение
Манипуляции с текстом для создания фрагментов и неполноты.

### Функции

#### `fragment_sentence(text: str) -> str`
Обрезает предложение на случайном месте.

#### `extract_random_word(text: str) -> str`
Извлекает случайное слово.

#### `reduce_text(text: str, reduction_level: float) -> str`
Удаляет случайные слова.

#### `truncate_mid_sentence(text: str) -> str`
Обрезает текст на середине предложения.

#### `ellipsis_replace(text: str) -> str`
Заменяет части текста многоточиями.

### Пример реализации

```python
import random
import re

def fragment_sentence(text: str) -> str:
    """Обрезает предложение на случайном месте."""
    if len(text) < 10:
        return text
    
    cut_point = random.randint(5, len(text) - 2)
    return text[:cut_point] + "..."

def extract_random_word(text: str) -> str:
    """Извлекает случайное слово из текста."""
    words = text.split()
    
    if not words:
        return ""
    
    # Предпочитаем существительные и глаголы (самые длинные слова)
    significant_words = [w for w in words if len(w) > 3]
    
    if significant_words:
        return random.choice(significant_words).strip(".,!?;:")
    
    return random.choice(words).strip(".,!?;:")

def reduce_text(text: str, reduction_level: float = 0.5) -> str:
    """Удаляет случайные слова из текста.
    
    reduction_level: 0.0 (ничего не удалять) до 1.0 (удалить все)
    """
    words = text.split()
    
    if not words:
        return ""
    
    keep_count = max(1, int(len(words) * (1 - reduction_level)))
    
    # Сохранить порядок слов
    indices = sorted(random.sample(range(len(words)), keep_count))
    kept_words = [words[i] for i in indices]
    
    return " ".join(kept_words)

def truncate_mid_sentence(text: str) -> str:
    """Обрезает текст на середине предложения."""
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    first_sentence = sentences[0]
    
    if len(first_sentence) > 10:
        mid_point = len(first_sentence) // 2
        return first_sentence[:mid_point] + "..."
    
    return fragment_sentence(text)

def ellipsis_replace(text: str, replacement_prob: float = 0.3) -> str:
    """Заменяет части текста многоточиями."""
    words = text.split()
    
    result = []
    for word in words:
        if random.random() < replacement_prob:
            result.append("...")
        else:
            result.append(word)
    
    return " ".join(result)

def abstract_text(text: str) -> str:
    """Превращает текст в абстракцию."""
    abstractions = [
        "...",
        "отсутствие",
        "пустота",
        "молчание",
        "тишина",
        "ничто"
    ]
    return random.choice(abstractions)
```

---

## 11. `src/utils/randomness.py` - Рандомизация промптов

### Статус
✅ **Реализовано** (см. текущий код)

### Основные функции
- `random_prompt(name, **kwargs)` - загрузка промпта
- `random_prompt_block(name, **kwargs)` - случайный блок из промпта
- `safe_format(text, **kwargs)` - безопасное форматирование

---

## 12. `src/config/config.env` - Переменные окружения

### Содержание

```env
# ==========================================
# Star_Void Configuration
# ==========================================

# LLM API Settings
# ==========================================
LLM_PROVIDER=openai          # openai, anthropic, local
MODEL_NAME=gpt-4             # gpt-3.5-turbo, gpt-4, claude-3-opus-20240229
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# LLM Parameters
# ==========================================
MAX_TOKENS=150               # Максимум токенов в ответе
TEMPERATURE=0.7              # Креативность (0.0 - 1.0)

# Behavior Settings
# ==========================================
SILENCE_PROBABILITY=0.2      # Базовая вероятность молчания (0.0 - 1.0)
VOID_SPEAK_PROBABILITY=0.05  # Вероятность спонтанного высказывания в void

# Filters
# ==========================================
MAX_RESPONSE_LENGTH=200      # Максимальная длина ответа (символы)
ENABLE_ADVICE_FILTER=true    # Фильтр советов
ENABLE_EMPATHY_FILTER=true   # Фильтр эмпатии

# Delays
# ==========================================
MIN_DELAY_SEC=0.5            # Минимальная задержка перед ответом
MAX_DELAY_SEC=2.0            # Максимальная задержка перед ответом
TYPING_SPEED_CPS=30          # Скорость печати (символов в секунду)

# Logging
# ==========================================
ENABLE_LOGGING=false         # Включить логирование
LOG_FILE=logs/star_void.log  # Путь к файлу логов
```

---

## Интеграция всех модулей

### Полный поток данных

```
1. Пользователь вводит текст в mailn.py
                ↓
2. mailn.py определяет режим и вызывает соответствующий модуль
                ↓
3. Модуль (ask/distort/void/silence) вызывает responder.respond()
                ↓
4. responder.py:
   - Проверяет silence.should_be_silent()
   - Загружает промпты через randomness.random_prompt()
   - Вызывает call_llm()
   - Применяет filters (advice, empathy, length)
                ↓
5. Для distort: дополнительно text.fragment_sentence() и т.д.
                ↓
6. delay.random_delay() - пауза перед выводом
                ↓
7. delay.typing_effect() - эффект печати
                ↓
8. Вывод ответа или молчание
```

### Пример полного взаимодействия

```python
# mailn.py
user_input = input("> ")
random_delay()
response = ask(user_input)
if response:
    typing_effect(response)

# ask.py
def ask(user_input):
    return respond(user_input, mode="ask")

# responder.py
def respond(user_input, mode):
    if should_be_silent(user_input, mode):
        return None
    
    prompt = random_prompt(mode)
    raw = call_llm(prompt, user_input)
    filtered = filter_advice(filter_empathy(raw))
    return filtered

# Результат: "А что значит 'дальше'?"
```

---

## Тестирование

### Примеры тестов

```python
# test_filters.py
def test_filter_advice():
    text = "Попробуй выйти на прогулку"
    result = filter_advice(text)
    assert "Попробуй" not in result

# test_silence.py
def test_should_be_silent_with_ellipsis():
    result = should_be_silent("...", "ask")
    # Должно быть True в большинст