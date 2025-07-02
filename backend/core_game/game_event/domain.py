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
from typing import Optional, Dict, List

class BaseGameEvent:
    """Common functionality for domain event wrappers.
    """

    def __init__(self, model: GameEventModel):
        self._data = model

    @property
    def id(self) -> str:
        """Return the unique identifier of the underlying event model."""
        return self._data.id


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

        if model:
            self._populate_from_model(model)
        else:
            self._all_events = {}

    def _populate_from_model(self, model: GameEventsManagerModel):
        """
        Iterates through the data models from the input, instantiates the correct
        domain wrapper for each, and populates the internal event dictionary.
        """
        self._all_events = {}
        for event_id, event_model in model.all_events.items():
            wrapper_class = WRAPPER_MAP.get(event_model.type)

            if wrapper_class:
                domain_event = wrapper_class(model=event_model)
                self._all_events[event_id] = domain_event
            else:
                print(f"Warning: Unknown event type '{event_model.type}' with ID '{event_id}' encountered. Skipping.")