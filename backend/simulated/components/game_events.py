from __future__ import annotations
import os

from typing import Set, List, Optional, Dict, Any, Union, TYPE_CHECKING

from core_game.game_event.domain import GameEventsManager

if TYPE_CHECKING:
    from core_game.game_event.domain import (
        BaseGameEvent,
    )   

from copy import deepcopy


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
        event = self._working_state.find_event(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
            
        if event.status in ["RUNNING", "COMPLETED"]:
            raise ValueError(f"Cannot link new conditions to event '{event_id}'. It is already in '{event.status}' status.")
        
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

    def disable_event(self, event_id: str) -> BaseGameEvent:
        event = self._working_state.find_event(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        if event.status != "AVAILABLE":
            raise ValueError(
                f"Event '{event_id}' must be AVAILABLE to be disabled."
            )
        return self._working_state.disable_event(event_id)

    def enable_event(self, event_id: str) -> BaseGameEvent:
        event = self._working_state.find_event(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        if event.status not in ["DISABLED", "COMPLETED"]:
            raise ValueError(
                f"Event '{event_id}' must be DISABLED or COMPLETED to be enabled."
            )
        return self._working_state.enable_event(event_id)

    def get_initial_summary(self) -> str:
        """
        Returns a formatted string summarizing all game events, grouped by narrative beat and then by status.
        """
        grouped_events = self._working_state.get_all_events_grouped()
        summary_lines = ["Summary (For more details use query tools):"]

        if not grouped_events:
            summary_lines.append("- No events currently defined.")
            return "\n".join(summary_lines)

        # Sort beats for consistent output (e.g., "BEATLESS" first, then by ID)
        sorted_beats = sorted(grouped_events.keys(), key=lambda x: (x != "BEATLESS", x))

        for beat_id in sorted_beats:
            status_groups = grouped_events[beat_id]
            beat_title = f"Narrative Beat: {beat_id}" if beat_id != "BEATLESS" else "Events without a specific Beat (BEATLESS)"
            summary_lines.append(f"\n## {beat_title}")

            # Sort statuses for consistent output (e.g., AVAILABLE, RUNNING, COMPLETED, DISABLED)
            sorted_statuses = sorted(status_groups.keys(), key=lambda x: (
                x != "AVAILABLE", x != "RUNNING", x != "COMPLETED", x != "DISABLED", x
            ))

            for status in sorted_statuses:
                events_in_status = status_groups[status]
                summary_lines.append(f"### Status: {status}")
                if not events_in_status:
                    summary_lines.append("  - No events in this status.")
                else:
                    # Sort events by ID or title for consistent display
                    sorted_events = sorted(events_in_status, key=lambda e: e.id)
                    for event in sorted_events:
                        summary_lines.append(f"  - Event ID: {event.id}")
                        summary_lines.append(f"    Title: {event.title}")
                        summary_lines.append(f"    Description: {event.description}")
                        summary_lines.append(f"    Type: {event.type}")
                        if event.activation_conditions:
                            conditions_summary = ", ".join([cond.model_data.type for cond in event.activation_conditions])
                            summary_lines.append(f"    Activation Conditions: {conditions_summary}")
                        else:
                            summary_lines.append("    Activation Conditions: None")

        return "\n".join(summary_lines)