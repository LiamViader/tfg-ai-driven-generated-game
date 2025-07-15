from __future__ import annotations

from copy import deepcopy

from core_game.character.schemas import CharactersModel
from core_game.map.schemas import GameMapModel
from core_game.game_event.schemas import GameEventsManagerModel
from simulated.game_state import SimulatedGameState
from simulated.versioning.deltas.checkpoints.base import StateCheckpointBase

class ChangesetCheckpoint(StateCheckpointBase):
    """
    Snapshot containing the necessary data to generate a changeset
    for an external consumer.
    """
    map_snapshot: GameMapModel
    characters_snapshot: CharactersModel
    game_events_snapshot: GameEventsManagerModel
    
    @classmethod
    def create(cls, state: SimulatedGameState) -> ChangesetCheckpoint:
        map_model = deepcopy(state.read_only_map.get_state().to_model())
        char_model = deepcopy(state.read_only_characters.get_state().to_model())
        events_model = deepcopy(state.read_only_events.get_state().to_model())
        return cls(map_snapshot=map_model, characters_snapshot=char_model, game_events_snapshot=events_model)