# режим диалога

from typing import Optional
from src.ai.responder import respond 

def ask (user_input: str) -> Optional[str]:
    
    return respond(user_input, mode = "ask")
