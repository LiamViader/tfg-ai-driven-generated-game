from __future__ import annotations

from copy import deepcopy
from simulated.components.characters import SimulatedCharacters
from simulated.components.map import SimulatedMap
from typing import Dict, Set, Any, Optional
from pydantic import BaseModel
from core_game.character.schemas import (
    CharactersModel,
    CharacterBaseModel,
    PlayerCharacterModel,
    NonPlayerCharacterModel,
)
from core_game.map.schemas import GameMapModel, ScenarioModel
from simulated.game_state import SimulatedGameState
from typing import Any
from uuid import uuid4
from simulated.versioning.schemas import (
    ScenarioDiffModel,
    CharacterDiffModel,
    DiffResultModel,
    ChangeDetailModel,
    ConnectionDiffModel,
)

def _model_dump(value: Any) -> Any:
    """
    Safely dump a value. If it's a Pydantic model, dump it to a dict.
    Otherwise, return the value as is. This makes it safe to use with
    any attribute type (e.g., int, str, or another model).
    """
    if isinstance(value, BaseModel):
        if hasattr(value, "model_dump"):
            return value.model_dump()
        return value.dict() 
    return value


def _characters_as_dict(model: CharactersModel) -> Dict[str, CharacterBaseModel]:
    registry = dict(model.registry)
    if model.player_character is not None:
        registry[model.player_character.id] = model.player_character
    return registry


class StateCheckpoint:
    """Snapshot of map and characters at a point in time."""

    def __init__(self, map_snapshot: GameMapModel, characters_snapshot: CharactersModel) -> None:
        self.map_snapshot = map_snapshot
        self.characters_snapshot = characters_snapshot

    @classmethod
    def create(cls, state: SimulatedGameState) -> "StateCheckpoint":
        map_model = deepcopy(state.read_only_map.get_state().to_model())
        char_model = deepcopy(state.read_only_characters.get_state().to_model())
        return cls(map_model, char_model)

    # ------------------------------------------------------------------
    # Diff helpers
    # ------------------------------------------------------------------
    def _get_scenario_visual_changes(
        self, old_s: ScenarioModel, new_s: ScenarioModel
    ) -> Optional[Dict[str, ChangeDetailModel]]:
        """Checks for differences in visual attributes between two scenarios."""
        visual_attributes = [
            "visual_description",
            "type",
            "zone",
            "indoor_or_outdoor",
        ]
        visual_changes: Dict[str, ChangeDetailModel] = {}
        for attr in visual_attributes:
            old_val = getattr(old_s, attr)
            new_val = getattr(new_s, attr)
            if old_val != new_val:
                visual_changes[attr] = ChangeDetailModel(old=old_val, new=new_val)
        
        return visual_changes if visual_changes else None

    def _get_connection_changes(
        self, old_s: ScenarioModel, new_s: ScenarioModel
    ) -> Optional[ConnectionDiffModel]:
        """Checks for differences in connections between two scenarios."""
        if old_s.connections != new_s.connections:
            conn_diff = self._diff_connections(old_s.connections, new_s.connections)
            return ConnectionDiffModel(**conn_diff) if conn_diff else None
        return None
    
    def _get_character_visual_changes(
        self, old_c: CharacterBaseModel, new_c: CharacterBaseModel
    ) -> Optional[Dict[str, ChangeDetailModel]]:
        """
        Checks for differences in visual attributes between two characters.
        """
        # Define which top-level attributes are considered "visual".
        visual_attributes = [
            "identity",
            "physical",
        ]
        visual_changes: Dict[str, ChangeDetailModel] = {}
        for attr in visual_attributes:
            old_val = getattr(old_c, attr)
            new_val = getattr(new_c, attr)
            # Since these attributes are Pydantic models, we compare their dumped dicts.
            if _model_dump(old_val) != _model_dump(new_val):
                visual_changes[attr] = ChangeDetailModel(
                    old=_model_dump(old_val), new=_model_dump(new_val)
                )

    def _get_character_location_changes(
        self, old_c: CharacterBaseModel, new_c: CharacterBaseModel
    ) -> Optional[ChangeDetailModel]:
        """Checks for differences in location between two characters."""
        if old_c.present_in_scenario != new_c.present_in_scenario:
            return ChangeDetailModel(
                old=old_c.present_in_scenario, new=new_c.present_in_scenario
            )
        return None

    def _diff_connections(self, old_conn: Dict[Any, Any], new_conn: Dict[Any, Any]) -> Dict[str, Any]:
        result = {"added": {}, "removed": {}, "changed": {}}
        keys = set(old_conn.keys()) | set(new_conn.keys())
        for key in keys:
            o = old_conn.get(key)
            n = new_conn.get(key)
            if o == n:
                continue
            if o is None:
                result["added"][key] = n
            elif n is None:
                result["removed"][key] = o
            else:
                result["changed"][key] = {"old": o, "new": n}
        if not any(result.values()):
            return {}
        return result

    def diff_scenarios_against(self, new_map: GameMapModel) -> ScenarioDiffModel:
        """
        Compares the scenarios from the checkpoint against a new map state,
        identifying added, removed, and modified scenarios with detailed changes.
        """
        old = self.map_snapshot.scenarios
        new = new_map.scenarios
        old_ids: Set[str] = set(old.keys())
        new_ids: Set[str] = set(new.keys())

        diff_dict: Dict[str, Any] = {
            "added": sorted(list(new_ids - old_ids)),
            "removed": sorted(list(old_ids - new_ids)),
            "modified": [],
            "modified_visual_info": {},
            "modified_connections": {},
        }

        for sid in old_ids & new_ids:
            old_s = old[sid]
            new_s = new[sid]

            if _model_dump(old_s) == _model_dump(new_s):
                continue

            # If any part of the model changed, mark it as modified.
            diff_dict["modified"].append(sid)

            # --- Call Helper Functions ---
            visual_changes = self._get_scenario_visual_changes(old_s, new_s)
            if visual_changes:
                diff_dict["modified_visual_info"][sid] = visual_changes

            connection_changes = self._get_connection_changes(old_s, new_s)
            if connection_changes:
                diff_dict["modified_connections"][sid] = connection_changes
        
        diff_dict["modified"].sort()
        return ScenarioDiffModel(**diff_dict)

    def diff_scenarios(self, state: SimulatedGameState) -> ScenarioDiffModel:
        current_map = state.read_only_map.get_state().to_model()
        return self.diff_scenarios_against(current_map)

    def diff_characters_against(
        self, new_chars_model: CharactersModel
    ) -> CharacterDiffModel:
        """
        Compares the characters from the checkpoint against a new character state,
        identifying added, removed, and modified characters with detailed changes.
        """
        old_chars = _characters_as_dict(self.characters_snapshot)
        new_chars = _characters_as_dict(new_chars_model)
        old_ids: Set[str] = set(old_chars.keys())
        new_ids: Set[str] = set(new_chars.keys())

        diff_dict: Dict[str, Any] = {
            "added": sorted(list(new_ids - old_ids)),
            "removed": sorted(list(old_ids - new_ids)),
            "modified": [],
            "modified_visual_info": {},
            "modified_location": {},
        }

        for cid in old_ids & new_ids:
            old_c = old_chars[cid]
            new_c = new_chars[cid]

            if _model_dump(old_c) == _model_dump(new_c):
                continue

            diff_dict["modified"].append(cid)

            # --- Call Helper Functions ---
            visual_changes = self._get_character_visual_changes(old_c, new_c)
            if visual_changes:
                diff_dict["modified_visual_info"][cid] = visual_changes

            location_changes = self._get_character_location_changes(old_c, new_c)
            if location_changes:
                diff_dict["modified_location"][cid] = location_changes
        
        diff_dict["modified"].sort()
        return CharacterDiffModel(**diff_dict)

    def diff_characters(self, state: SimulatedGameState) -> CharacterDiffModel:
        current_chars = state.read_only_characters.get_state().to_model()
        return self.diff_characters_against(current_chars)


class StateCheckpointManager:
    """Utility class to manage creation and diff of checkpoints."""

    def __init__(self, state: SimulatedGameState) -> None:
        self._state = state
        self._checkpoints: Dict[str, StateCheckpoint] = {}

    def create_checkpoint(self, checkpoint_id: Optional[str] = None) -> str:
        """Create a checkpoint and return its identifier.

        If ``checkpoint_id`` is ``None`` a UUID will be generated automatically.
        """
        if checkpoint_id is None:
            checkpoint_id = str(uuid4())
        if checkpoint_id in self._checkpoints:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' already exists")
        self._checkpoints[checkpoint_id] = StateCheckpoint.create(self._state)
        return checkpoint_id

    def get_checkpoint(self, checkpoint_id: str) -> StateCheckpoint:
        if checkpoint_id not in self._checkpoints:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' not found")
        return self._checkpoints[checkpoint_id]

    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Remove a stored checkpoint to free memory."""
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
        else:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' not found")

    def diff(
        self,
        from_checkpoint: str,
        to_checkpoint: str | None = None,
    ) -> DiffResultModel:
        cp_from = self.get_checkpoint(from_checkpoint)
        if to_checkpoint is None:
            map_model = self._state.read_only_map.get_state().to_model()
            chars_model = self._state.read_only_characters.get_state().to_model()
        else:
            cp_to = self.get_checkpoint(to_checkpoint)
            map_model = cp_to.map_snapshot
            chars_model = cp_to.characters_snapshot

        return DiffResultModel(
            scenarios=cp_from.diff_scenarios_against(map_model),
            characters=cp_from.diff_characters_against(chars_model),
        )
