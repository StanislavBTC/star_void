# обрезка, фрагментация


def fragment_sentence(text: str) -> str:
    """Обрезает предложение на случ
        text: Текст для фрагментации

    Returns:
        Обрезанный текст с многоточием
    """
    # TODO: Реализовать фрагментацию
    # См. docs/MODULE_SPECS.md раздел #10 для полного кода
    return text


def extract_random_word(text: str) -> str:
    """Извлекает случайное слово из текста.

    Args:
        text: Исходный текст

    Returns:
        Одно случайное слово
    """
    # TODO: Реализовать извлечение слова
    # См. docs/MODULE_SPECS.md раздел #10 для полного кода
    words = text.split()
    return words[0] if words else ""


def reduce_text(text: str, reduction_level: float = 0.5) -> str:
    """Удаляет случайные слова из текста.

    Args:
        text: Исходный текст
        reduction_level: Уровень редукции (0.0 - 1.0)

    Returns:
        Текст с удаленными словами
    """
    # TODO: Реализовать редукцию текста
    # См. docs/MODULE_SPECS.md раздел #10 для полного кода
    return text


def truncate_mid_sentence(text: str) -> str:
    """Обрезает текст на середине предложения.

    Args:
        text: Исходный текст

    Returns:
        Обрезанный текст
    """
    # TODO: Реализовать обрезку
    # См. docs/MODULE_SPECS.md раздел #10 для полного кода
    return text
