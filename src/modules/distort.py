# режим искажения
from typing import Optional

from src.ai.responder import respond


def distort(user_input: str) -> Optional[str]:
    """Режим искажения - фрагментация, растворение смысла.

    Args:
        user_input: Текст от пользователя

    Returns:
        Искаженный ответ или None (молчание)
    """
    # TODO: Реализовать режим distort с применением text.py
    # См. docs/MODULE_SPECS.md раздел #6 для полного кода
    return respond(user_input, mode="distort")
