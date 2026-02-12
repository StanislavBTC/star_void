# пост-фильтры (длина, эмпатия, "советы")

import random
import os
from dotenv import load_dotenv

load_dotenv("config/config.env")
BASE_SILENCE_PROBABILITY = float(os.getenv("SILENCE_PROBABILITY", '0.2'))

SILENCE_PATTERNS = [
    
    "...",
    "- - -",
    "",
    "   ",
    "."
]

MODE_MULTIPLIERS = {
    
    "ask": 1.0,
    "distort": 1.5,
    "void": 2.0,
    "silence": float('inf')
    
}

def should_be_silent(user_input: str, mode: str = "ask") -> bool:
    
    if mode == "silence":
        return True
        
    if user_input.strip() in SILENCE_PATTERNS:
        return random.random() < 0.5
        
    probability = BASE_SILENCE_PROBABILITY * MODE_MULTIPLIERS.get(mode, 1.0)
    
    probability = min(probability, 0.95)
    
    return random.random() > probability 
    
def should_void_speak() -> bool:

    void_speak_prob = float(os.getenv("VOID_SPEAK_PROBABILITY", 0.02))
    return random.random() < void_speak_prob


import re

def filter_thinking(text: str) -> str:
    """Удаляет блок размышлений <think>...</think> из ответа."""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


def filter_advice(text: str) -> str:
    """Фильтр для удаления советов."""
    if not os.getenv("ENABLE_ADVICE_FILTER", "true").lower() == "true":
        return text
    
    # Удалить явные советы
    advice_indicators = ["лучше", "следует", "рекомендую", "нужно", "стоит"]
    lines = text.split('\n')
    filtered_lines = []
    
    for line in lines:
        if not any(indicator in line.lower() for indicator in advice_indicators):
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines)


def filter_empathy(text: str) -> str:
    """Фильтр для удаления эмпатичных фраз."""
    if not os.getenv("ENABLE_EMPATHY_FILTER", "true").lower() == "true":
        return text
    
    empathy_phrases = [
        "понимаю", "сочувствую", "чувствую", "мне жаль", 
        "я с вами", "вы не один", "всё будет хорошо"
    ]
    
    for phrase in empathy_phrases:
        text = text.replace(phrase, "...")
        
    return text


def filter_length(text: str) -> str:
    """Фильтр для ограничения длины ответа."""
    max_len = int(os.getenv("MAX_RESPONSE_LENGTH", "200"))
    
    if len(text) <= max_len:
        return text
    
    return text[:max_len] + "..."
    
