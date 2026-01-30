# режим диалога
from typing import Optional

from src.ai.responder import respond


def ask(user_input: str) -> Optional[str]:
    """Режим диалога - краткие ответы, вопросы, дистанция.

    Args:
        user_input: Текст от пользователя

    Returns:
        Ответ ИИ или None (молчание)
    """
    # TODO: Реализовать режим ask
    # См. docs/MODULE_SPECS.md раздел #5 для полного кода
    return respond(user_input, mode="ask")
