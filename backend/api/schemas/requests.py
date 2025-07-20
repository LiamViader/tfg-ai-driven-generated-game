from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class GenerationRequest(BaseModel):
    user_prompt: str = Field(default="Improvise")


class ActionType(str, Enum):
    """Enumeration for the different types of player actions."""
    MOVE_PLAYER = "MOVE_PLAYER"
    TRIGGER_EVENT = "TRIGGER_ACTIVATION_CONDITION"


class ActionPayload(BaseModel):
    """Flexible payload for different action types."""
    new_scenario_id: Optional[str] = None
    activation_condition_id: Optional[str] = None
    # You can add more fields for future actions (e.g., item_id, target_id)

class ActionRequest(BaseModel):
    """The request sent by the client for any action."""
    from_checkpoint_id: str
    action_type: ActionType
    payload: ActionPayload