from __future__ import annotations
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, Optional, Type
from uuid import uuid4
from pydantic import BaseModel
from simulated.game_state import SimulatedGameState

# --- 1. Clase Base Abstracta ---
class StateCheckpointBase(BaseModel, ABC):
    """Base class for any type of state snapshot."""
    
    @classmethod
    @abstractmethod
    def create(cls, state: SimulatedGameState) -> StateCheckpointBase:
        """Factory method to create a checkpoint instance."""
        pass