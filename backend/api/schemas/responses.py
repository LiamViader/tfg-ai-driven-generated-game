from pydantic import BaseModel
from typing import Dict, Any, Optional, Union, List
from enum import Enum

class FollowUpActionType(str, Enum):
    """Enumeration for the different types of follow-up actions for the client."""
    NONE = "NONE"
    START_NARRATIVE_STREAM = "START_NARRATIVE_STREAM"

class StartNarrativeStreamPayload(BaseModel):
    event_id: str
    involved_character_ids: List[str]

class FollowUpAction(BaseModel):
    """Instruction from the backend to the client on what to do next."""
    type: FollowUpActionType
    # The payload is now a Union of specific models, making it type-safe.
    payload: Union[StartNarrativeStreamPayload, None] = None

class ActionResponse(BaseModel):
    """The unified response for any player action."""
    changeset: Dict[str, Any]
    follow_up_action: FollowUpAction
    error: Optional[str] = None # NEW: Field to communicate errors