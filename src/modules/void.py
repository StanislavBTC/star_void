# пассивный режим
from typing import Optional

from src.ai.responder import respond


def void(user_input: str = "") -> Optional[str]:
    """Пассивный режим - фоновое присутствие, долгое молчание.

    Args:
        user_input: Текст от пользователя (опционально)

    Returns:
        Ответ ИИ или None (молчание)
    """
    # TODO: Реализовать режим void
    # См. docs/MODULE_SPECS.md раздел #7 для полного кода
    return respond(user_input, mode="void") if user_input else None
