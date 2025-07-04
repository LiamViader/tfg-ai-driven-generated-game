"""Domain classes for working with game event models."""

from .schemas import (
    NPCConversationEventModel,
    PlayerNPCConversationEventModel,
    NarratorInterventionEventModel,
    CutsceneFrameModel,
    CutsceneEventModel,
    NPCMessage,
    NarratorMessage,
    GameEventModel,
    GameEventsManagerModel,
)
from typing import Optional, Dict, List, Set
from collections import defaultdict
from .constants import EVENT_STATUSES, EVENT_STATUS_LITERAL
from core_game.game_event.activation_conditions.domain import (
    ActivationCondition,
    CharacterInteractionOption,
    WRAPPER_MAP as CONDITION_WRAPPER_MAP
)

class BaseGameEvent:
    """Common functionality for domain event wrappers.
    """

    def __init__(self, model: GameEventModel):
        self._data = model
        self.activation_conditions: List[ActivationCondition] = []
        self._build_condition_wrappers()

    def _build_condition_wrappers(self):
        """Instantiates domain objects for the activation conditions."""
        for condition_model in self._data.activation_conditions:
            wrapper_class = CONDITION_WRAPPER_MAP.get(condition_model.type)
            if wrapper_class:
                self.activation_conditions.append(wrapper_class(model=condition_model))

    @property
    def id(self) -> str:
        """Return the unique identifier of the underlying event model."""
        return self._data.id

    @property
    def status(self) -> str:
        """Returns the status"""
        return self._data.status
    
    @property
    def title(self) -> str:
        """Returns the title"""
        return self._data.title
    
    @property
    def description(self) -> str:
        """Returns the description"""
        return self._data.description
    
    def get_activation_conditions(self) -> List[ActivationCondition]:
        return self.activation_conditions

    def get_model(self) -> GameEventModel:
        """Return the underlying Pydantic model."""
        return self._data

class NPCConversationEvent(BaseGameEvent):
    """Domain logic for an NPC-only conversation."""

    def __init__(self, model: NPCConversationEventModel):
        self._data = model

    def add_message(self, message: NPCMessage) -> None:
        self._data.messages.append(message)


class PlayerNPCConversationEvent(BaseGameEvent):
    """Domain logic for a conversation involving the player and NPCs."""

    def __init__(self, model: PlayerNPCConversationEventModel):
        self._data = model

    def add_message(self, message: NPCMessage) -> None:
        self._data.messages.append(message)


class NarratorInterventionEvent(BaseGameEvent):
    """Domain logic for narrator interventions."""

    def __init__(self, model: NarratorInterventionEventModel):
        self._data = model

    def add_message(self, message: NarratorMessage) -> None:
        self._data.messages.append(message)


class CutsceneFrame:
    """Domain wrapper around :class:`CutsceneFrameModel`."""

    def __init__(self, model: CutsceneFrameModel):
        self._data: CutsceneFrameModel = model

    def add_narrator_message(self, message: NarratorMessage) -> None:
        self._data.narrator_messages.append(message)

    def add_npc_message(self, message: NPCMessage) -> None:
        self._data.npc_messages.append(message)


class CutsceneEvent(BaseGameEvent):
    """Domain logic for cutscene events."""

    def __init__(self, model: CutsceneEventModel):
        self._data = model

    def add_frame(self, frame: CutsceneFrameModel) -> None:
        self._data.frames.append(frame)


WRAPPER_MAP: Dict[str, type[BaseGameEvent]] = {
    "npc_conversation": NPCConversationEvent,
    "player_npc_conversation": PlayerNPCConversationEvent,
    "narrator_intervention": NarratorInterventionEvent,
    "cutscene": CutsceneEvent,
}

class GameEventsManager:
    """Domain class for managing and storing events"""
    def __init__(self, model: Optional[GameEventsManagerModel] = None):
        self._all_events: Dict[str, BaseGameEvent] = {}
        self._running_event_stack: List[str] = []

        self._status_indexes: Dict[str, Set[str]] = {status: set() for status in EVENT_STATUSES}
        self._events_by_beat_id: Dict[str, Set[str]] = defaultdict(set)
        self._beatless_event_ids: Set[str] = set()
        self._interaction_options_by_character: Dict[str, Set[str]] = defaultdict(set)
        
        if model:
            self._populate_and_reindex(model)

    def _populate_and_reindex(self, model: GameEventsManagerModel):
        """
        Populates the manager from the data model and REBUILDS all
        indexes from the primary data source (`all_events`).
        """
        self._running_event_stack = model.running_event_stack.copy()
        
        self._status_indexes = {status: set() for status in EVENT_STATUSES}
        self._events_by_beat_id = defaultdict(set)
        self._beatless_event_ids = set()
        self._interaction_options_by_character = defaultdict(set)
        self._all_events = {}

        for event_id, event_model in model.all_events.items():
            wrapper_class = WRAPPER_MAP.get(event_model.type)
            if not wrapper_class: continue
            
            domain_event = wrapper_class(model=event_model)
            self._all_events[event_id] = domain_event

            self._status_indexes[event_model.status].add(event_id)

            if event_model.source_beat_id:
                self._events_by_beat_id[event_model.source_beat_id].add(event_id)
            else:
                self._beatless_event_ids.add(event_id)

            for condition in domain_event.get_activation_conditions():
                if isinstance(condition, CharacterInteractionOption):
                    self._interaction_options_by_character[condition.character_id].add(event_id)



    def to_model(self) -> GameEventsManagerModel:
        return GameEventsManagerModel(
            all_events={eid: ev.get_model() for eid, ev in self._all_events.items()},
            running_event_stack=self._running_event_stack
        )
    
    # --- METHODS TO MANIPULATE THE STACK ---

    def start_event(self, event_id: str):
        """
        Activates an event, sets its status to RUNNING, and pushes it onto the top of the stack.
        """
        if event_id not in self._all_events:
            raise KeyError(f"Error: Cannot start non-existent event '{event_id}'.")
            
        event = self._all_events[event_id]
        if event.status != "AVAILABLE":
            return

        self.set_event_status(event_id, "RUNNING")
        self._running_event_stack.append(event_id)

    def complete_current_event(self):
        """
        Completes the event that is currently at the top of the stack,
        pops it, and updates its status to COMPLETED.
        """
        if not self._running_event_stack:
            print("Warning: Tried to complete an event, but the running stack is empty.")
            return

        event_id_to_complete = self._running_event_stack.pop()
        self.set_event_status(event_id_to_complete, "COMPLETED")
        
        # Optional: What happens to the event that was underneath? Does it resume?
        # The logic for resuming would be in the GameLoopManager.

    # --- METHODS TO QUERY THE STACK ---

    def get_current_running_event(self) -> Optional[BaseGameEvent]:
        """
        Returns the event that is currently active (at the top of the stack).
        Returns None if no event is running.
        """
        if not self.is_any_event_running():
            return None
        
        current_event_id = self._running_event_stack[-1]
        return self._all_events.get(current_event_id)

    def is_any_event_running(self) -> bool:
        """Returns True if the running event stack is not empty."""
        return len(self._running_event_stack) > 0

    def set_event_status(self, event_id: str, new_status: EVENT_STATUS_LITERAL):
        """
        Updates an event's status and correctly maintains the indexes.
        This is the ONLY method you should use to change an event's status.
        """
        if new_status not in EVENT_STATUSES:
            print(f"Error: Attempted to set invalid status '{new_status}'.")
            return

        if event_id in self._all_events:
            event = self._all_events[event_id]
            old_status = event.status

            if old_status == new_status:
                return 

            if old_status in self._status_indexes:
                self._status_indexes[old_status].discard(event_id)

            self._status_indexes[new_status].add(event_id)

            event.get_model().status = new_status
            print(f"Event '{event_id}' status changed from '{old_status}' to '{new_status}'.")

    def get_events_by_status(self, status: str) -> List[BaseGameEvent]:
        """
        Efficiently retrieves all events with a given status using the index.
        """
        if status not in self._status_indexes:
            return []
        
        event_ids = self._status_indexes[status]
        return [self._all_events[eid] for eid in event_ids]

    def get_completed_event_ids(self) -> Set[str]:
        """
        Directly and efficiently returns the set of completed event IDs.
        """
        return self._status_indexes.get("COMPLETED", set())
