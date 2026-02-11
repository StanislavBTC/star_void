# пассивный режим
from typing import Optional
import time 
import threading

from src.ai.responder import respond
from src.ai.silence import should_void_speak

def void(user_input: str = "") -> Optional[str]:
    
    if user_input and should_void_speak():
        return respond(user_input, mode = "void")
    return None

