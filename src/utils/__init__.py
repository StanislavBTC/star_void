# Utils Package
"""
Вспомогательные утилиты для Star_Void.

Модули:
    randomness: Рандомизация промптов, загрузка из файлов
    delay: Паузы перед ответом, эффект печати
    text: Фрагментация, обрезка, извлечение слов
"""

from .delay import random_delay, typing_effect
from .randomness import random_prompt, random_prompt_block, safe_format
from .text import (
    extract_random_word,
    fragment_sentence,
    reduce_text,
    truncate_mid_sentence,
)

__all__ = [
    # randomness
    "random_prompt",
    "random_prompt_block",
    "safe_format",
    # delay
    "random_delay",
    "typing_effect",
    # text
    "fragment_sentence",
    "extract_random_word",
    "reduce_text",
    "truncate_mid_sentence",
]
