from copy import deepcopy
from typing import List, Optional, Set

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
    NPCConversationEventModel,
    PlayerNPCConversationEventModel,
    NarratorInterventionEventModel,
    CutsceneEventModel,
    CutsceneFrameModel,
    NPCMessage,
    NarratorMessage,
)


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