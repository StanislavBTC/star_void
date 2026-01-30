# Modules Package
"""
Режимы работы Star_Void.

Модули:
    ask: Режим диалога (краткие ответы, вопросы, дистанция)
    distort: Режим искажения (фрагментация, растворение смысла)
    void: Пассивный режим (фоновое присутствие, молчание)
    silence: Режим полного молчания
"""

from .ask import ask
from .distort import distort
from .silence import silence
from .void import void

__all__ = [
    "ask",
    "distort",
    "void",
    "silence",
]
