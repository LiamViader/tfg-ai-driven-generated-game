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
        self._base_state = base_state  # <- Referencia al SimulatedGameState
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
        if not self.map:
            self._map = deepcopy(self.map)
            self.modified_components.add("map")
        return self.map

    def modify_characters(self) -> SimulatedCharacters:
        if not self.characters:
            self._characters = deepcopy(self.characters)
            self.modified_components.add("characters")
        return self.characters
    
    def has_modified_map(self) -> bool:
        return self._map is not None

    def get_modified_map(self) -> SimulatedMap:
        assert self._map is not None, "get_modified_map() called without modification"
        return self._map

    def set_modified_map(self, new_map: SimulatedMap):
        self._map = new_map

    def has_modified_characters(self) -> bool:
        return self._characters is not None

    def get_modified_characters(self) -> SimulatedCharacters:
        assert self._characters is not None, "get_modified_characters() called without modification"
        return self._characters

    def set_modified_characters(self, new_characters: SimulatedCharacters):
        self._characters = new_characters