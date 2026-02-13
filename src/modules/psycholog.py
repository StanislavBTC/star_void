from typing import Optional
from src.ai.responder import respond

def psycholog(user_input: str) -> Optional[str]:

    return respond(user_input, mode = "psycholog")