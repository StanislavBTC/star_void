# паузы, медленность
import os
import time
import random
from dotenv import load_dotenv

load_dotenv("config/config.env")

MIN_DELAY = float(os.getenv("MIN_DELAY_SEC", "0.5"))
MAX_DELAY = float(os.getenv("MAX_DELAY_SEC", "2.0"))
TYPING_SPEED = int(os.getenv("TYPING_SPEED_CPS", "30"))    

def random_delay(min_sec: float = MIN_DELAY, max_sec: float = MAX_DELAY) -> None:
 
    time.sleep(random.uniform(min_sec, max_sec))

def typing_effect(text: str, chars_per_second: int = TYPING_SPEED) -> None:
    
    for char in text:
        print(char, end = '', flush = True)
        time.sleep(1 / chars_per_second)
        
    print()
    
def weighted_delay(user_input: str) -> None:
    """Задержка зависит от длины ввода пользователя."""
    base_delay = MIN_DELAY
    input_length_factor = len(user_input) * 0.01
    calculated_delay = base_delay + input_length_factor
    time.sleep(min(calculated_delay, MAX_DELAY))
    

def thinking_animation(duration: float = 2.0) -> None:
    """Анимация 'мышления' с точками."""
    import sys
    
    # Use the duration parameter or calculate based on config
    total_duration = duration
    dots_count = 0
    
    while total_duration > 0:
        # Show thinking animation
        sys.stdout.write('\r' + '.' * ((dots_count % 4) + 1))
        sys.stdout.flush()
        time.sleep(0.5)
        total_duration -= 0.5
        dots_count += 1
    
    # Clear the line
    sys.stdout.write('\r')
    sys.stdout.flush()
    