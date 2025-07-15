from __future__ import annotations

from copy import deepcopy

from pydantic import BaseModel
from core_game.character.schemas import (
    CharactersModel
)
from core_game.map.schemas import GameMapModel
from simulated.game_state import SimulatedGameState
from versioning.deltas.checkpoints.base import StateCheckpointBase

class InternalStateCheckpoint(StateCheckpointBase):
    """Snapshot with specific data for internal processes (e.g., image re-rendering)."""
    map_snapshot: GameMapModel
    characters_snapshot: CharactersModel
    
    @classmethod
    def create(cls, state: SimulatedGameState) -> InternalStateCheckpoint:
        map_model = deepcopy(state.read_only_map.get_state().to_model())
        char_model = deepcopy(state.read_only_characters.get_state().to_model())
        return cls(map_snapshot=map_model, characters_snapshot=char_model)