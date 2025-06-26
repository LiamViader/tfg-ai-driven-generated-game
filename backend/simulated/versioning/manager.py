# nueva-clase/game_state_version_manager.py

from core_game.game_state.singleton import GameStateSingleton
from core_game.game_state.domain import GameState
from simulated.components.map import SimulatedMap
from simulated.components.characters import SimulatedCharacters
from simulated.versioning.layer import SimulationLayer # Importamos la clase SimulationLayer
from typing import List, Optional

class GameStateVersionManager:
    """
    Manages the versioning of the game state through layers (transactions).
    Its sole responsibility is to handle begin, commit, and rollback operations.
    """
    def __init__(self, game_state: GameState):
        self._base_map = SimulatedMap(game_state.game_map)
        self._base_characters = SimulatedCharacters(game_state.characters)
        self._layers: List[SimulationLayer] = []

    @property
    def base_map(self) -> SimulatedMap:
        return self._base_map
    
    @property
    def base_characters(self) -> SimulatedCharacters:
        return self._base_characters

    def begin_transaction(self):
        """Starts a new transaction layer."""
        parent = self._layers[-1] if self._layers else None
        self._layers.append(SimulationLayer(parent=parent, version_manager=self))

    def commit(self):
        """Commits the changes from the current layer to its parent or the base state."""
        if not self._layers:
            raise RuntimeError("No simulation layer to commit.")
        
        layer = self._layers.pop()
        parent = self._layers[-1] if self._layers else None

        if layer.has_modified_map():
            if parent:
                parent.set_modified_map(layer.get_modified_map())
            else:
                self._base_map = layer.get_modified_map()
                self._sync_map_to_domain()

        if layer.has_modified_characters():
            if parent:
                parent.set_modified_characters(layer.get_modified_characters())
            else:
                self._base_characters = layer.get_modified_characters()
                self._sync_characters_to_domain()

    def rollback(self):
        """Discards all changes in the current transaction layer."""
        if not self._layers:
            raise RuntimeError("No active simulation layers to rollback.")
        self._layers.pop()


    def get_current_map(self, for_writing: bool = False) -> SimulatedMap:
        """Gets the current map state. If for_writing, ensures it's a mutable copy."""
        layer = self._layers[-1] if self._layers else None
        if not layer:
            return self._base_map
        
        return layer.modify_map() if for_writing else layer.map

    def get_current_characters(self, for_writing: bool = False) -> SimulatedCharacters:
        """Gets the current characters state. If for_writing, ensures it's a mutable copy."""
        layer = self._layers[-1] if self._layers else None
        if not layer:
            return self._base_characters
        
        return layer.modify_characters() if for_writing else layer.characters

    def _sync_map_to_domain(self):
        game_state = GameStateSingleton.get_instance()
        game_state.update_map(self._base_map.get_state())

    def _sync_characters_to_domain(self):
        game_state = GameStateSingleton.get_instance()
        game_state.update_characters(self._base_characters.get_state())