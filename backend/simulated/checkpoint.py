from copy import deepcopy
from simulated.characters import SimulatedCharacters
from simulated.map import SimulatedMap
from simulated.game_state import SimulatedGameState
from typing import Any


class StateCheckpointManager:
    def __init__(self):
        self.snapshots: dict[str, dict[str, Any]] = {}

    def create_checkpoint(self, checkpoint_id: str, simulated_state: SimulatedGameState):
        self.snapshots[checkpoint_id] = {
            "map": deepcopy(simulated_state.map.working_state.to_model()),
            "characters": deepcopy(simulated_state.characters.working_state.to_model()),
        }

    def diff_from_checkpoint(self, checkpoint_id: str, simulated_state: SimulatedGameState) -> dict[str, Any]:
        if checkpoint_id not in self.snapshots:
            raise ValueError(f"Checkpoint {checkpoint_id} no encontrado.")

        current_map = simulated_state.map.working_state.to_model()
        saved_map = self.snapshots[checkpoint_id]["map"]

        current_chars = simulated_state.characters.working_state.to_model()
        saved_chars = self.snapshots[checkpoint_id]["characters"]

        return {
            "map": self._diff_maps(saved_map, current_map),
            "characters": self._diff_characters(saved_chars, current_chars)
        }

    def _diff_maps(self, old_map_model, new_map_model) -> dict[str, Any]:
        changes = {
            "added_scenarios": [],
            "removed_scenarios": [],
            "modified_scenarios": []
        }

        old = old_map_model.scenarios
        new = new_map_model.scenarios

        for sid in new:
            if sid not in old:
                changes["added_scenarios"].append(sid)
            elif new[sid].dict() != old[sid].dict():
                changes["modified_scenarios"].append(sid)

        for sid in old:
            if sid not in new:
                changes["removed_scenarios"].append(sid)

        return changes
    
    def _diff_characters(self, old, new):
        # lógica análoga para comparar personajes