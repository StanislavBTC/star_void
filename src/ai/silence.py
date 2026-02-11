# логика намеренного молчания
import os
import time
import random
from dotenv import load_dotenv

from src.ai.filters import BASE_SILENCE_PROBABILITY

load_dotenv("src/config/config.env")

BASE_SILENCE_PROBABILITY = float(os.getenv("SILENCE_PROBABILITY", "0.25"))

SILENS_PATTERNS = {
    
    "...",
    "..",
    ".",
    "   "
}

MODE_MULTIPLIERS = {
    
    "ask": 1.0,
    "distort": 1.5,
    "void": 4.0,
    "silence": float("inf")
}

def should_be_silent(user_input: str, mode: str = "ask") -> bool:
    
    if mode == "silence":
        return True    
    
    if user_input.strip() in SILENS_PATTERNS:
        return random.random()  < 0.8
        
    probability = BASE_SILENCE_PROBABILITY * MODE_MULTIPLIERS.get(mode, 1.0)

    probability = min(probability, 0.95)
    
    return random.random() < probability
    
def should_void_speak() -> bool:
    void_speak_prob = float(os.getenv("VOID_SPEAK_PROBABILITY", "0.05"))
    return random.random() < void_speak_prob