# Quick Start Guide - Star_Void

Быстрый старт для начала разработки прямо сейчас.

---

## 📦 Шаг 1: Установка зависимостей (5 минут)

```bash
# Перейти в директорию проекта
cd star_void

# Создать виртуальное окружение (опционально)
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
pip install openai python-dotenv
```

---

## 🔑 Шаг 2: Настройка API ключа (5 минут)

### Вариант A: OpenAI (рекомендуется для начала)

1. Зарегистрируйтесь на https://platform.openai.com
2. Создайте API ключ в разделе "API Keys"
3. Скопируйте шаблон конфигурации:
   ```bash
   cp env.example src/config/config.env
   ```
4. Откройте `src/config/config.env` и вставьте ключ:
   ```env
   OPENAI_API_KEY=sk-ваш-ключ-здесь
   LLM_PROVIDER=openai
   MODEL_NAME=gpt-3.5-turbo
   ```

### Вариант B: Anthropic (Claude)

```env
ANTHROPIC_API_KEY=sk-ant-ваш-ключ-здесь
LLM_PROVIDER=anthropic
MODEL_NAME=claude-3-haiku-20240307
```

### Вариант C: Локальная модель (Ollama)

```bash
# Установить Ollama: https://ollama.ai
ollama pull llama2
```

```env
LLM_PROVIDER=local
MODEL_NAME=llama2
```

---

## 🛠️ Шаг 3: Первая реализация - responder.py (1-2 часа)

Откройте `src/ai/responder.py` и замените содержимое:

```python
import os
from typing import Optional
from dotenv import load_dotenv
from src.utils.randomness import random_prompt
from src.ai.filters import filter_length, filter_advice, filter_empathy

load_dotenv("src/config/config.env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "150"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

def respond(user_input: str, mode: str = "ask") -> Optional[str]:
    """Генерация ответа ИИ."""
    
    # Загрузка промптов
    core_prompt = random_prompt("core")
    mode_prompt = random_prompt(mode)
    system_prompt = f"{core_prompt}\n\n{mode_prompt}"
    
    # Вызов LLM
    try:
        raw_response = call_llm(system_prompt, user_input)
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None
    
    # Фильтры
    filtered = filter_advice(raw_response)
    filtered = filter_empathy(filtered)
    filtered = filter_length(filtered, 200)
    
    return filtered.strip() if filtered.strip() else None

def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Вызов LLM API."""
    if LLM_PROVIDER == "openai":
        return call_openai(system_prompt, user_prompt)
    # TODO: добавить другие провайдеры
    raise ValueError(f"Провайдер {LLM_PROVIDER} не реализован")

def call_openai(system_prompt: str, user_prompt: str) -> str:
    """OpenAI API."""
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.ChatCompletion.create(
        model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    
    return response.choices[0].message.content
```

**Тест:**
```python
python -c "from src.ai.responder import respond; print(respond('Привет'))"
```

Если видите ответ - отлично! Переходите к следующему шагу.

---

## 🤫 Шаг 4: Логика молчания - silence.py (30 минут)

Откройте `src/ai/silence.py`:

```python
import random
import os
from dotenv import load_dotenv

load_dotenv("src/config/config.env")

BASE_SILENCE_PROBABILITY = float(os.getenv("SILENCE_PROBABILITY", "0.2"))

SILENCE_PATTERNS = ["...", "…", "."]

MODE_MULTIPLIERS = {
    "ask": 1.0,
    "distort": 1.5,
    "void": 4.0,
    "silence": float('inf')
}

def should_be_silent(user_input: str, mode: str = "ask") -> bool:
    """Решает, нужно ли молчать."""
    
    if mode == "silence":
        return True
    
    if user_input.strip() in SILENCE_PATTERNS:
        return random.random() < 0.8
    
    probability = BASE_SILENCE_PROBABILITY * MODE_MULTIPLIERS.get(mode, 1.0)
    
    if len(user_input.strip()) < 5:
        probability *= 1.5
    
    probability = min(probability, 0.95)
    
    return random.random() < probability
```

**Интеграция в responder.py:**

Добавьте в начало функции `respond()`:
```python
from src.ai.silence import should_be_silent

def respond(user_input: str, mode: str = "ask") -> Optional[str]:
    # Проверка молчания
    if should_be_silent(user_input, mode):
        return None
    # ... остальной код
```

---

## 🚀 Шаг 5: Запуск программы - обновление mailn.py (30 минут)

Замените содержимое `mailn.py`:

```python
from src.ai.responder import respond

def main() -> None:
    print("""
╔════════════════════════════════════════╗
║           S T A R _ V O I D            ║
╚════════════════════════════════════════╝

Терминальный софт на Python.
Это программа для паузы.

> A terminal space where answers are optional

Команды: /help, /quit
""")

    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            if user_input == "/quit":
                print("\nGoodbye!")
                break
            
            if user_input == "/help":
                print("\n/quit - выход из программы\n")
                continue
            
            # Получить ответ
            response = respond(user_input)
            
            # Вывод
            if response:
                print(f"< {response}\n")
            # Если None - молчание
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Ошибка: {e}\n")

if __name__ == "__main__":
    main()
```

**Запуск:**
```bash
python mailn.py
```

**Поздравляю! У вас работает базовая версия Star_Void! 🎉**

---

## ✨ Шаг 6: Добавление эффектов (1 час)

### 6.1 Создать `src/utils/delay.py`:

```python
import time
import random
import os
from dotenv import load_dotenv

load_dotenv("src/config/config.env")

MIN_DELAY = float(os.getenv("MIN_DELAY_SEC", "0.5"))
MAX_DELAY = float(os.getenv("MAX_DELAY_SEC", "2.0"))
TYPING_SPEED = int(os.getenv("TYPING_SPEED_CPS", "30"))

def random_delay(min_sec: float = MIN_DELAY, max_sec: float = MAX_DELAY):
    time.sleep(random.uniform(min_sec, max_sec))

def typing_effect(text: str, chars_per_second: int = TYPING_SPEED):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(1 / chars_per_second)
    print()
```

### 6.2 Обновить `mailn.py`:

```python
from src.utils.delay import random_delay, typing_effect

# В функции main, после получения ответа:
response = respond(user_input)

if response:
    random_delay()  # Пауза перед ответом
    typing_effect(response)  # Эффект печати
```

**Запуск:**
```bash
python mailn.py
```

Теперь ответы появляются с паузой и печатаются посимвольно!

---

## 🎭 Шаг 7: Режимы работы (2 часа)

### 7.1 Режим ask - `src/modules/ask.py`:

```python
from typing import Optional
from src.ai.responder import respond

def ask(user_input: str) -> Optional[str]:
    return respond(user_input, mode="ask")
```

### 7.2 Режим distort - `src/modules/distort.py`:

Сначала создайте `src/utils/text.py`:

```python
import random

def extract_random_word(text: str) -> str:
    words = [w for w in text.split() if len(w) > 3]
    if not words:
        words = text.split()
    return random.choice(words).strip(".,!?;:") if words else ""

def fragment_sentence(text: str) -> str:
    if len(text) < 10:
        return text
    cut_point = random.randint(5, len(text) - 2)
    return text[:cut_point] + "..."
```

Затем `src/modules/distort.py`:

```python
from typing import Optional
from src.ai.responder import respond
from src.utils.text import extract_random_word, fragment_sentence
import random

def distort(user_input: str) -> Optional[str]:
    response = respond(user_input, mode="distort")
    
    if not response:
        return None
    
    methods = [
        lambda: extract_random_word(response),
        lambda: fragment_sentence(response),
        lambda: "...",
        lambda: None
    ]
    
    return random.choice(methods)()
```

### 7.3 Режим void - `src/modules/void.py`:

```python
from typing import Optional

def void(user_input: str = "") -> None:
    return None  # Всегда молчание
```

### 7.4 Режим silence - `src/modules/silence.py`:

```python
from typing import Optional

def silence(user_input: str = "") -> None:
    return None
```

### 7.5 Обновить `mailn.py` с режимами:

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

Режимы: /ask, /distort, /void, /silence
Команды: /help, /quit
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
            
            if user_input.startswith("/"):
                command = user_input[1:].lower()
                
                if command in ["quit", "exit"]:
                    print("\nGoodbye!")
                    break
                
                if command in modes:
                    mode = command
                    print(f"→ режим: {mode}\n")
                    continue
                
                if command == "help":
                    print("""
Режимы:
  /ask      - диалог (краткие ответы, вопросы)
  /distort  - искажение (фрагменты, абстракция)
  /void     - пустота (молчание)
  /silence  - только молчание

Команды:
  /help - справка
  /quit - выход
""")
                    continue
            
            random_delay()
            response = modes[mode](user_input)
            
            if response:
                typing_effect(response)
                print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Ошибка: {e}\n")

if __name__ == "__main__":
    main()
```

---

## 🎉 Готово! У вас полнофункциональный Star_Void!

### Запуск:

```bash
python mailn.py
```

### Примеры использования:

```
[ask] > Привет
[пауза...]
< А что тебе нужно?

[ask] > /distort
→ режим: distort

[distort] > Я чувствую себя потерянным
[пауза...]
< потерянным...

[distort] > /silence
→ режим: silence

[silence] > Привет
[молчание]

[silence] > /quit
Goodbye!
```

---

## 📊 Чек-лист готовности

- [x] Установлены зависимости
- [x] API ключ настроен
- [x] responder.py работает
- [x] silence.py работает
- [x] mailn.py запускается
- [x] Эффекты (паузы, печать) работают
- [x] Все 4 режима работают
- [x] Команды работают

**Вы создали MVP за ~4-5 часов работы! 🚀**

---

## 🔄 Что дальше?

1. **Протестируйте все режимы** - поговорите с программой
2. **Настройте вероятности** в `config.env`
3. **Добавьте свои промпты** в `src/config/ai/`
4. **Читайте ROADMAP.md** для дальнейшего развития
5. **Следуйте MODULE_SPECS.md** для улучшений

---

## 🐛 Частые проблемы

### "ModuleNotFoundError: No module named 'openai'"
```bash
pip install openai
```

### "No API key provided"
Проверьте `src/config/config.env` - ключ должен быть там.

### "Rate limit exceeded"
Добавьте задержки или переключитесь на GPT-3.5-turbo.

### Программа не видит модули
Убедитесь, что запускаете из корневой директории:
```bash
cd star_void
python mailn.py
```

---

## 📚 Документация

- `PROJECT_STRUCTURE.md` - подробное описание всех файлов
- `TREE.md` - визуальная структура
- `MODULE_SPECS.md` - детальные спецификации модулей
- `ROADMAP.md` - план развития проекта

---

**Приятного погружения в пустоту! ✨**

> A terminal space where answers are optional