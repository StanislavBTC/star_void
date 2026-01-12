# Утилиты для рандомизации промптов из src/config/ai

import random
from pathlib import Path
from typing import List, Optional, Any

BASE_DIR = Path(__file__).resolve().parents[2]
AI_PROMPTS_DIR = BASE_DIR / "src" / "config" / "ai"


class SafeFormatter:
    """Helper to format strings safely, ignoring missing keys."""
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getitem__(self, key):
        return self.kwargs.get(key, "{" + key + "}")


def safe_format(text: str, **kwargs: Any) -> str:
    """Форматирует строку, подставляя значения из kwargs.
    Если ключа нет, оставляет плейсхолдер как есть.
    """
    if not kwargs:
        return text
    # Используем str.format_map с кастомным dict для безопасноcти
    # Однако стандартный format_map все равно кинет KeyError для отсутствующих ключей,
    # если не использовать специальный класс-обертку или defaultdict.
    # Простой вариант для Python modern:
    
    # 1. Сначала пытаемся отформатировать стандартно, если все ключи есть
    try:
        return text.format(**kwargs)
    except KeyError:
        # 2. Если каких-то ключей нет, можно сделать частичное форматирование
        # или просто вернуть текст, если мы хотим быть супер-строгими.
        # Но задача - "safe format".
        
        # Реализуем простой replace для переданных ключей, чтобы не ломаться на фигурных скобках JSON
        # Это менее мощно чем .format (нет спецификаторов), но надежнее для промптов с кодом.
        result = text
        for k, v in kwargs.items():
            result = result.replace(f"{{{k}}}", str(v))
        return result


def rand_choice(seq):
    """Возвращает случайный элемент из последовательности."""
    if not seq:
        return None
    return random.choice(seq)


def list_prompt_files() -> List[Path]:
    """Вернуть список .txt файлов в папке `src/config/ai`.

    Порядок отсортирован для детерминированности при тестировании.
    """
    if not AI_PROMPTS_DIR.exists():
        return []
    return sorted([p for p in AI_PROMPTS_DIR.iterdir() if p.is_file() and p.suffix == ".txt"])


def read_prompt_file(path: Path, **kwargs) -> str:
    """Прочитать файл промта как текст (utf-8).
    Возвращает пустую строку, если файл не существует.
    Поддерживает подстановку переменных через `kwargs`.
    """
    try:
        text = path.read_text(encoding="utf-8").strip()
        return safe_format(text, **kwargs)
    except Exception:
        return ""


def random_prompt_file() -> Optional[Path]:
    """Выбрать случайный файл-промт из папки `src/config/ai`.
    Возвращает `Path` или `None`, если файлов нет.
    """
    files = list_prompt_files()
    if not files:
        return None
    return random.choice(files)


def random_prompt(name: Optional[str] = None, **kwargs) -> str:
    """Вернуть текст случайного промта.

    - Если `name` указан (например, 'ask' или 'core'), попытается найти файл `name.txt`.
    - Иначе выберет случайный файл в папке.
    - `kwargs` используются для форматирования текста промпта.
    """
    if name:
        candidate = AI_PROMPTS_DIR / f"{name}.txt"
        if candidate.exists():
            return read_prompt_file(candidate, **kwargs)

    chosen = random_prompt_file()
    if not chosen:
        return ""
    return read_prompt_file(chosen, **kwargs)


def random_prompt_block(name: Optional[str] = None, **kwargs) -> str:
    """Если файл содержит несколько блоков, выбрать случайный.
    
    Разделители:
    - `---` (три дефиса на отдельной строке)
    - `\n\n` (двойной перевод строки) - как запасной вариант

    Полезно для файлов, где внутри хранится несколько вариантов.
    """
    text = random_prompt(name, **kwargs)
    if not text:
        return ""
    
    # Приоритет разделителю "---"
    if "\n---\n" in text:
        blocks = [b.strip() for b in text.split("\n---\n") if b.strip()]
    elif "\n\n" in text:
        blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    else:
        blocks = [text]

    if not blocks:
        return text
        
    return random.choice(blocks)
