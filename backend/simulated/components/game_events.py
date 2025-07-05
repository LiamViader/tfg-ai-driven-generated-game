from copy import deepcopy
from typing import List, Optional, Set, Dict

from core_game.game_event.domain import (
    GameEventsManager,
    BaseGameEvent,
    NPCConversationEvent,
    PlayerNPCConversationEvent,
    NarratorInterventionEvent,
    CutsceneEvent,
    CutsceneFrame,
)
from core_game.game_event.schemas import (
    GameEventModel
)
from core_game.game_event.activation_conditions.schemas import ActivationConditionModel

class SimulatedGameEvents:
    """Lightweight wrapper around :class:`GameEventsManager`."""

    def __init__(self, events: GameEventsManager) -> None:
        self._working_state: GameEventsManager = events

    def __deepcopy__(self, memo):
        copied = GameEventsManager(model=deepcopy(self._working_state.to_model()))
        return SimulatedGameEvents(copied)

    def get_state(self) -> GameEventsManager:
        return self._working_state
    
    def get_completed_event_ids(self) -> Set[str]:
        return self._working_state.get_completed_event_ids()
    
    def get_current_running_event(self) -> Optional[BaseGameEvent]:
        return self._working_state.get_current_running_event()
    
    def add_event(self, event_model: GameEventModel) -> BaseGameEvent:
        """
        Performs event-specific validation and then adds the event to the manager.
        """
        if event_model.id in self._working_state._all_events:
            raise ValueError(f"Event with ID '{event_model.id}' already exists.")
        
        return self._working_state.add_and_index_event(event_model)
    
    def find_event(self, event_id: str) -> Optional[BaseGameEvent]:
        """Returns the base game event associated to that id"""
        return self._working_state.find_event(event_id)
    
    def link_conditions_to_event(self, event_id: str, conditions: List[ActivationConditionModel]):
        """
        Performs event-specific validation before delegating the linking logic.
        """
        if not self._working_state.find_event(event_id):
            raise KeyError(f"Event with ID '{event_id}' not found.")

        self._working_state.link_conditions_to_event(event_id, conditions)

    def unlink_condition_from_event(self, event_id: str, condition_id: str) -> ActivationConditionModel:
        """Delegates removal of a specific activation condition from an event."""
        if not self._working_state.find_event(event_id):
            raise KeyError(f"Event with ID '{event_id}' not found.")
        return self._working_state.unlink_condition_from_event(event_id, condition_id)


    def list_events(self, status: Optional[str] = None) -> List[BaseGameEvent]:
        """Delegates event listing to the manager."""
        return self._working_state.list_events(status)

    def get_all_events_grouped(self) -> Dict[str, Dict[str, List[BaseGameEvent]]]:
        """Delegates grouping logic to the manager."""
        return self._working_state.get_all_events_grouped()

    def delete_event(self, event_id: str) -> BaseGameEvent:
        event = self._working_state.find_event(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        return self._working_state.delete_event(event_id)

    def update_event_description(self, event_id: str, new_description: str) -> BaseGameEvent:
        if not self._working_state.find_event(event_id):
            raise KeyError(f"Event with ID '{event_id}' not found.")
        return self._working_state.update_event_description(event_id, new_description)

    def update_event_title(self, event_id: str, new_title: str) -> BaseGameEvent:
        if not self._working_state.find_event(event_id):
            raise KeyError(f"Event with ID '{event_id}' not found.")
        return self._working_state.update_event_title(event_id, new_title)
