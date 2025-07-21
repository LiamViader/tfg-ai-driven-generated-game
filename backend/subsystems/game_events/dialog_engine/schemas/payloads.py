from pydantic import BaseModel
from typing import Literal, Optional

class TurnDecision(BaseModel):
    """
    Defines the expected JSON structure from the LLM for deciding the next speaker.
    """
    # The next speaker ID is now optional. If the LLM returns null, the conversation ends.
    next_speaker_id: Optional[str] = None
    reasoning: str
