from pydantic import BaseModel, Field
from typing import Literal, Union

class BaseTriggerModel(BaseModel):
    """Base class for all trigger models."""
    # This field identifies the trigger's type.
    type: str 

class AreaEntryTrigger(BaseTriggerModel):
    """Triggers when the player enters a specific scenario."""
    type: Literal["area_entry"] = "area_entry"
    scenario_id: str = Field(..., description="The ID of the scenario that triggers the event upon entry.")

class DialogueChoiceTrigger(BaseTriggerModel):
    """Triggers when a specific dialogue option is chosen."""
    type: Literal["dialogue_choice"] = "dialogue_choice"
    source_event_id: str = Field(..., description="The ID of the conversation event that contains the option.")
    # You could use an option ID or the exact text of the option for the identifier.
    option_identifier: str = Field(..., description="A unique identifier for the dialogue option that triggers this event.")

class EventCompletionTrigger(BaseTriggerModel):
    """Triggers when another event is completed."""
    type: Literal["event_completion"] = "event_completion"
    source_event_id: str = Field(..., description="The ID of the event that must be completed to activate this one.")

class DirectorCommandTrigger(BaseTriggerModel):
    """Triggers by a direct command from the 'Director' agent or the system."""
    type: Literal["director_command"] = "director_command"
    # This type may not need additional data; its type is the information itself.

GameEventTrigger = Union[
    AreaEntryTrigger,
    DialogueChoiceTrigger,
    EventCompletionTrigger,
    DirectorCommandTrigger,
]