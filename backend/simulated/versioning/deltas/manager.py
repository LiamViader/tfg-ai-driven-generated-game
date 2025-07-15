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

class StateCheckpointManager:
    """
    Manages the lifecycle of checkpoints, holding a reference 
    to the game state it operates on.
    """
    
    def __init__(self, state: SimulatedGameState) -> None:
        """
        Initializes the manager with a specific game state instance.
        """
        self._state: SimulatedGameState = state
        self._checkpoints: Dict[str, StateCheckpointBase] = {}

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
