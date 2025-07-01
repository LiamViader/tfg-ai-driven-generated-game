from typing import Optional, TYPE_CHECKING
from simulated.components.map import SimulatedMap
from simulated.components.characters import SimulatedCharacters
from simulated.components.game_session import SimulatedGameSession
from simulated.components.relationships import SimulatedRelationships
from simulated.components.narrative import SimulatedNarrative
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
        self._relationships: Optional[SimulatedRelationships] = None
        self._session: Optional[SimulatedGameSession] = None
        self._narrative: Optional[SimulatedNarrative] = None

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

    @property
    def session(self) -> SimulatedGameSession:
        if self._session:
            return self._session
        elif self.parent:
            return self.parent.session
        else:
            return self._version_manager.base_session

    @property
    def relationships(self) -> SimulatedRelationships:
        if self._relationships:
            return self._relationships
        elif self.parent:
            return self.parent.relationships
        else:
            return self._version_manager.base_relationships

    @property
    def narrative(self) -> SimulatedNarrative:
        if self._narrative:
            return self._narrative
        elif self.parent:
            return self.parent.narrative
        else:
            return self._version_manager.base_narrative
        
    def modify_map(self) -> SimulatedMap:
        if self._map is None:
            self._map = deepcopy(self.map)
        return self._map

    def modify_characters(self) -> SimulatedCharacters:
        if self._characters is None:
            self._characters = deepcopy(self.characters)
        return self._characters

    def modify_session(self) -> SimulatedGameSession:
        if self._session is None:
            self._session = deepcopy(self.session)
        return self._session

    def modify_relationships(self) -> SimulatedRelationships:
        if self._relationships is None:
            self._relationships = deepcopy(self.relationships)
        return self._relationships

    def modify_narrative(self) -> SimulatedNarrative:
        if self._narrative is None:
            self._narrative = deepcopy(self.narrative)
        return self._narrative
    
    def has_modified_map(self) -> bool:
        return self._map is not None

    def get_modified_map(self) -> SimulatedMap:
        return self._map or self.map

    def set_modified_map(self, new_map: SimulatedMap):
        self._map = new_map

    def has_modified_characters(self) -> bool:
        return self._characters is not None

    def has_modified_session(self) -> bool:
        return self._session is not None

    def has_modified_relationships(self) -> bool:
        return self._relationships is not None

    def has_modified_narrative(self) -> bool:
        return self._narrative is not None

    def get_modified_characters(self) -> SimulatedCharacters:
        return self._characters or self.characters

    def get_modified_session(self) -> SimulatedGameSession:
        return self._session or self.session

    def get_modified_relationships(self) -> SimulatedRelationships:
        return self._relationships or self.relationships

    def get_modified_narrative(self) -> SimulatedNarrative:
        return self._narrative or self.narrative

    def set_modified_characters(self, new_characters: SimulatedCharacters):
        self._characters = new_characters

    def set_modified_session(self, new_session: SimulatedGameSession):
        self._session = new_session

    def set_modified_relationships(self, new_relationships: SimulatedRelationships):
        self._relationships = new_relationships

    def set_modified_narrative(self, new_narrative: SimulatedNarrative):
        self._narrative = new_narrative
