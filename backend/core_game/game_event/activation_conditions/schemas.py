from pydantic import BaseModel, Field
from typing import Literal, Union

_condition_id_counter = 0


def generate_condition_id() -> str:
    """Return a sequential id of the form 'condition_001'."""
    global _condition_id_counter
    _condition_id_counter += 1
    return f"condition_{_condition_id_counter:03d}"


def rollback_condition_id() -> None:
    global _condition_id_counter
    _condition_id_counter -= 1

class ActivationConditionModel(BaseModel):
    """Base class for all activation condition models."""
    id: str = Field(default_factory=generate_condition_id, description="Unique identifier for the activation condition.")
    type: str

class AreaEntryConditionModel(ActivationConditionModel):
    """Activates when the player enters a specific scenario."""
    type: Literal["area_entry"] = "area_entry"
    scenario_id: str = Field(..., description="The ID of the scenario that activates the event upon entry.")

class EventCompletionConditionModel(ActivationConditionModel):
    """Activates after another event completion."""
    type: Literal["event_completion"] = "event_completion"
    source_event_id: str = Field(..., description="The ID of the event that must be COMPLETED to activate this one.")

class ImmediateActivationModel(ActivationConditionModel):
    """Causes an event to activate automatically immediately, This condition has the highest execution priority. If another event is already running, this one will preempt it by being pushed to the top of the event stack. The previous event is effectively paused and will only resume after this immediate event is completed."""
    type: Literal["immediate"] = "immediate"

class CharacterInteractionOptionModel(ActivationConditionModel):
    """Makes an event available as a menu option when the player interacts with a specific character."""
    type: Literal["character_interaction"] = "character_interaction"
    character_id: str = Field(..., description="The ID of the character the player must interact with to see this option.")
    menu_label: str = Field(..., description="The text that will appear in the UI for the player to select. E.g., 'Ask about the stolen artifact', 'About the raising war', 'What time is it?', etc.")
    is_repeatable: bool = Field(False, description="If true, this option will reappear in the catalog even after the event has been completed, so the player can keep playing this interaction.")

