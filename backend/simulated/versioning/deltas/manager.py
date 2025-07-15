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
from simulated.versioning.deltas.checkpoints.base import StateCheckpointBase
from typing import Dict, Optional, Type
from simulated.versioning.deltas.detectors.changeset.root_changeset import ChangesetDetector
from simulated.versioning.deltas.detectors.internal.root_internal import InternalDiffDetector
from simulated.versioning.deltas.checkpoints.changeset import ChangesetCheckpoint
from simulated.versioning.deltas.checkpoints.internal import InternalStateCheckpoint
from simulated.versioning.deltas.schemas import DiffResultModel

class StateCheckpointManager:
    """
    Manages the lifecycle of checkpoints, holding a reference 
    to the game state it operates on.
    """
    
    def __init__(
        self,
        state: SimulatedGameState,
        default_changeset_detector: ChangesetDetector,
        default_internal_diff_detector: InternalDiffDetector
    ):
        self._state = state
        self._checkpoints: Dict[str, StateCheckpointBase] = {}
        
        self._default_changeset_detector = default_changeset_detector
        self._default_internal_diff_detector = default_internal_diff_detector

    def create_checkpoint(
        self,
        checkpoint_type: Type[StateCheckpointBase],
        checkpoint_id: Optional[str] = None
    ) -> str:
        """
        Creates a checkpoint of a specific type from the stored game state.
        
        Args:
            checkpoint_type: The class of the checkpoint to create.
            checkpoint_id: An optional ID for the checkpoint.
        
        Returns:
            The ID of the created checkpoint.
        """
        if checkpoint_id is None:
            checkpoint_id = str(uuid4())
        
        if checkpoint_id in self._checkpoints:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' already exists")
        
        self._checkpoints[checkpoint_id] = checkpoint_type.create(self._state)
        return checkpoint_id

    def get_checkpoint(self, checkpoint_id: str) -> StateCheckpointBase:
        """
        Retrieves a checkpoint by its ID.
        
        Returns the base type. You may need to check its instance type
        if you need to access specific subclass fields.
        """
        if checkpoint_id not in self._checkpoints:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' not found")
        return self._checkpoints[checkpoint_id]

    def delete_checkpoint(self, checkpoint_id: str) -> None:
        """Removes a stored checkpoint to free up memory."""
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
        else:
            raise RuntimeError(f"Checkpoint '{checkpoint_id}' not found")


    def generate_changeset(
        self, 
        from_id: str, 
        to_id: Optional[str] = None,
        detector_override: Optional[ChangesetDetector] = None
    ) -> Dict[str, Any] | None:
        """
        Generates a client-facing changeset.

        Compares the 'from_id' checkpoint against the 'to_id' checkpoint.
        If 'to_id' is None, it compares against the current live state.
        """
        cp_from_base = self.get_checkpoint(from_id)
        if not isinstance(cp_from_base, ChangesetCheckpoint):
            raise TypeError("Changeset generation requires a 'ChangesetCheckpoint' as its origin ('from_id').")
        cp_from = cp_from_base

        if to_id is not None:
            cp_to_base = self.get_checkpoint(to_id)
            if not isinstance(cp_to_base, ChangesetCheckpoint):
                raise TypeError("When 'to_id' is provided, it must also be a 'ChangesetCheckpoint'.")
            cp_to = cp_to_base
        else:
            cp_to = ChangesetCheckpoint.create(self._state)

        detector_to_use = detector_override if detector_override is not None else self._default_changeset_detector
                
        return detector_to_use.detect(cp_from, cp_to)

    def generate_internal_diff(
        self, 
        from_id: str, 
        to_id: Optional[str] = None,
        detector_override: Optional[InternalDiffDetector] = None
    ) -> DiffResultModel:
        """
        Generates an internal diff report.

        Compares the 'from_id' checkpoint against the 'to_id' checkpoint.
        If 'to_id' is None, it compares against the current live state.
        """
        cp_from_base = self.get_checkpoint(from_id)
        if not isinstance(cp_from_base, InternalStateCheckpoint):
            raise TypeError("Internal diff generation requires an 'InternalStateCheckpoint' as its origin ('from_id').")
        cp_from = cp_from_base

        if to_id is not None:
            cp_to_base = self.get_checkpoint(to_id)
            if not isinstance(cp_to_base, InternalStateCheckpoint):
                raise TypeError("When 'to_id' is provided, it must also be an 'InternalStateCheckpoint'.")
            cp_to = cp_to_base
        else:
            cp_to = InternalStateCheckpoint.create(self._state)

        detector_to_use = detector_override if detector_override is not None else self._default_internal_diff_detector
            
        return detector_to_use.detect(cp_from, cp_to)