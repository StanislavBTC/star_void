# обрезка, фрагментация
import random
import re

def fragment_sentence(text: str) -> str:
    if len(text) == 0:
        return "i'm dead?"
        
    if len(text) < 8:
        return text
        
    if len(text) <= 9:
        cut_point = random.randint(5, len(text) - 2)
        return text[:cut_point] + "..."

    cut_point = random.randint(7, len(text) - 3)
    return text[:cut_point] + "..."


def extract_random_word(text: str) -> str:
    word = text.split()
    
    if not word:
        return"tsss"

    signifficant_word = [w for w in word if len(w) > 3]

    if signifficant_word:
        return random.choice(signifficant_word).strip(f".,?!:;")
    
    return random.choice(word).strip(".,?!:;")
     
     
def reduce_text(text: str, reduction_level: float = 0.5) -> str:

    words = text.split()
    
    if not words:
        return ""
    
    keep_count = max(1, int(len(words) * (1 - reduction_level)))
    
    # Сохранить порядок слов
    indices = sorted(random.sample(range(len(words)), keep_count))
    kept_words = [words[i] for i in indices]
    
    return " ".join(kept_words)    

def truncate_mid_sentence(text: str) -> str:
    
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text
    
    first_sentence = sentences[0]
    
    if len(first_sentence) > 10:
        mid_point = len(first_sentence) // 2
        return first_sentence[:mid_point] + "..."
    
    return fragment_sentence(text)
    
def ellipsis_replace(text: str, replacement_prob: float = 0.3) -> str:
    """Заменяет части текста многоточиями."""
    words = text.split()
    
    result = []
    for word in words:
        if random.random() < replacement_prob:
            result.append("...")
        else:
            result.append(word)
    
    return " ".join(result)

def abstract_text(text: str) -> str:
    """Превращает текст в абстракцию."""
    abstractions = [
        "...",
        "отсутствие",
        "пустота",
        "молчание",
        "тишина",
        "ничто"
    ]
    return random.choice(abstractions)
