# AI Core Package
"""
Ядро системы ИИ для Star_Void.

Модули:
    responder: Единая точка взаимодействия с LLM API
    filters: Пост-фильтры для очистки ответов
    silence: Логика принятия решений о молчании
"""

from .filters import filter_advice, filter_empathy, filter_length
from .responder import respond
from .silence import should_be_silent

__all__ = [
    "respond",
    "filter_advice",
    "filter_empathy",
    "filter_length",
    "should_be_silent",
]
