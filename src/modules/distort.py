# режим искажения
import random
from pydoc import text
from typing import Optional
from src.ai.responder import respond
from src.utils.text import (
    fragment_sentence,
    extract_random_word,
    reduce_text,
    truncate_mid_sentence
)

    
def distort(user_input: str) -> Optional[str]:

    distorted = fragment_sentence(user_input)
    if len(distorted) > 10:
        distorted = reduce_text(distorted, 0.3)
    elif "..." not in distorted:
        distorted = truncate_mid_sentence(distorted)
    
    # Добавляем немного рандомности
    if len(distorted) > 5 and random.random() < 0.3:
        distorted = extract_random_word(distorted)
    
    return respond(distorted, mode="distort") if distorted else None

