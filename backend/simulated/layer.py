from typing import Optional, TYPE_CHECKING
from simulated.map import SimulatedMap
from simulated.characters import SimulatedCharacters
if TYPE_CHECKING:
    from simulated.game_state import SimulatedGameState
from copy import deepcopy

class SimulationLayer:
    def __init__(
        self, 
        parent: Optional['SimulationLayer'], 
        base_state: 'SimulatedGameState'
    ):
        self.parent = parent
        self._base_state = base_state 
        self._map: Optional[SimulatedMap] = None
        self._characters: Optional[SimulatedCharacters] = None
        self.modified_components = set()

    @property
    def map(self) -> SimulatedMap:
        if self._map:
            return self._map
        elif self.parent:
            return self.parent.map
        else:
            return self._base_state.base_map

    @property
    def characters(self) -> SimulatedCharacters:
        if self._characters:
            return self._characters
        elif self.parent:
            return self.parent.characters
        else:
            return self._base_state.base_characters
        
    def modify_map(self) -> SimulatedMap:
        if self._map is None:
            self._map = deepcopy(self.map)
            self.modified_components.add("map")
        return self._map

    def modify_characters(self) -> SimulatedCharacters:
        if self._characters is None:
            self._characters = deepcopy(self.characters)
            self.modified_components.add("characters")
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