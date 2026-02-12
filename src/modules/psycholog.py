from typing import Optional
from src.ai.responder import respond

def psycholog(user_inpyt: str) -> Optional[str]:
    
    return respond(user_inpyt, mode = "psycholog")