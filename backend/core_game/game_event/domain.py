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

class BaseGameEvent:
    """Common functionality for domain event wrappers.
    """

    def __init__(self, model: GameEventModel):
        self._data = model

    @property
    def id(self) -> str:
        """Return the unique identifier of the underlying event model."""
        return self._data.id

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


WRAPPER_MAP = {
    "npc_conversation": NPCConversationEvent,
    "player_npc_conversation": PlayerNPCConversationEvent,
    "narrator_intervention": NarratorInterventionEvent,
    "cutscene": CutsceneEvent,
}

class GameEventsManager:
    """Domain class for managing and storing events"""
    def __init__(self, model: Optional[GameEventsManagerModel] = None):
        self._all_events: Dict[str, BaseGameEvent]
        self.events_by_beat_id: Dict[str, Set[str]]
        self.beatless_event_ids: Set[str]

        if model:
            self._populate_from_model(model)
        else:
            self._all_events = {}
            self.events_by_beat_id = {}
            self.beatless_event_ids = set()

    def _populate_from_model(self, model: GameEventsManagerModel):
        """
        Iterates through the data models from the input, instantiates the correct
        domain wrapper for each, and populates the internal event dictionary.
        """
        self._all_events = {}
        self.events_by_beat_id = {}
        self.beatless_event_ids = set()
        for event_id, event_model in model.all_events.items():
            wrapper_class = WRAPPER_MAP.get(event_model.type)

            if wrapper_class:
                domain_event = wrapper_class(model=event_model)
                self._all_events[event_id] = domain_event
            else:
                print(f"Warning: Unknown event type '{event_model.type}' with ID '{event_id}' encountered. Skipping.")

    #PER FER DE MANERA CORRECTA
    def add_event(self, event: BaseGameEvent) -> BaseGameEvent:
        if event.id in self._all_events:
            raise ValueError(f"Event with ID '{event.id}' already exists.")
        self._all_events[event.id] = event
        return event

    def to_model(self) -> GameEventsManagerModel:
        return GameEventsManagerModel(
            all_events={eid: ev.get_model() for eid, ev in self._all_events.items()}
        )


    #PER FER
    def get_initial_summary(self) -> str:
        if not self._all_events:
            return "No game events created yet."
        lines = [f"{eid} ({ev.get_model().type})" for eid, ev in self._all_events.items()]
        return f"Game events ({len(self._all_events)} total): " + ", ".join(lines)