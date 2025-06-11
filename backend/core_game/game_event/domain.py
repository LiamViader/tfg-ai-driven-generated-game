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
)


class BaseGameEvent:
    """Common functionality for domain event wrappers.

    Parameters
    ----------
    model:
        The Pydantic model storing the event data.
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
        super().__init__(model)

    def add_message(self, message: NPCMessage) -> None:
        self._data.messages.append(message)


class PlayerNPCConversationEvent(BaseGameEvent):
    """Domain logic for a conversation involving the player and NPCs."""

    def __init__(self, model: PlayerNPCConversationEventModel):
        super().__init__(model)

    def add_message(self, message: NPCMessage) -> None:
        self._data.messages.append(message)


class NarratorInterventionEvent(BaseGameEvent):
    """Domain logic for narrator interventions."""

    def __init__(self, model: NarratorInterventionEventModel):
        super().__init__(model)

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
        super().__init__(model)

    def add_frame(self, frame: CutsceneFrameModel) -> None:
        self._data.frames.append(frame)

