# пост-фильтры (длина, эмпатия, "советы")


def filter_length(text: str, max_length: int) -> str:
    """Обрезает текст до максимальной длины."""
    if len(text) > max_length:
        return text[:max_length]
    return text


def filter_advice(text: str) -> str:
    """Удаляет фразы, похожие на советы."""
    advice_markers = [
        "попробуй",
        "попробуйте",
        "рекомендую",
        "советую",
        "стоит",
        "лучше",
        "нужно",
        "следует",
    ]

    lines = text.split("\n")
    filtered_lines = []

    for line in lines:
        line_lower = line.lower()
        is_advice = any(marker in line_lower for marker in advice_markers)
        if not is_advice:
            filtered_lines.append(line)

    return "\n".join(filtered_lines)


def filter_empathy(text: str) -> str:
    """Удаляет излишне эмпатичные фразы."""
    empathy_phrases = [
        "я понимаю",
        "понимаю тебя",
        "я тебя понимаю",
        "сочувствую",
        "мне жаль",
        "это нормально",
        "не переживай",
        "всё будет хорошо",
    ]

    result = text
    for phrase in empathy_phrases:
        result = result.replace(phrase, "")
        result = result.replace(phrase.capitalize(), "")

    # Удаляем двойные пробелы и лишние переводы строк
    result = " ".join(result.split())

    return result.strip()
