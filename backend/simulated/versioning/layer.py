from typing import Optional, TYPE_CHECKING
from simulated.components.map import SimulatedMap
from simulated.components.characters import SimulatedCharacters
if TYPE_CHECKING:
    from simulated.versioning.manager import GameStateVersionManager
    from simulated.game_state import SimulatedGameState
from copy import deepcopy

class SimulationLayer:
    def __init__(
        self, 
        parent: Optional['SimulationLayer'], 
        version_manager: 'GameStateVersionManager'
    ):
        self.parent = parent
        self._version_manager = version_manager
        self._map: Optional[SimulatedMap] = None
        self._characters: Optional[SimulatedCharacters] = None

    @property
    def map(self) -> SimulatedMap:
        if self._map:
            return self._map
        elif self.parent:
            return self.parent.map
        else:
            return self._version_manager.base_map

    @property
    def characters(self) -> SimulatedCharacters:
        if self._characters:
            return self._characters
        elif self.parent:
            return self.parent.characters
        else:
            return self._version_manager.base_characters
        
    def modify_map(self) -> SimulatedMap:
        if self._map is None:
            self._map = deepcopy(self.map)
        return self._map

    def modify_characters(self) -> SimulatedCharacters:
        if self._characters is None:
            self._characters = deepcopy(self.characters)
        return self._characters
    
    def has_modified_map(self) -> bool:
        return self._map is not None

    def get_modified_map(self) -> SimulatedMap:
        return self._map or self.map

    def set_modified_map(self, new_map: SimulatedMap):
        self._map = new_map

    def has_modified_characters(self) -> bool:
        return self._characters is not None

    def get_modified_characters(self) -> SimulatedCharacters:
        return self._characters or self.characters

    def set_modified_characters(self, new_characters: SimulatedCharacters):
        self._characters = new_characters