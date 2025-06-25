from core_game.game.singleton import GameStateSingleton
from core_game.game.domain import GameState
from simulated.map import SimulatedMap
from simulated.characters import SimulatedCharacters
from simulated.layer import SimulationLayer
from typing import List, Tuple, Optional
from core_game.character.schemas import PlayerCharacterModel, rollback_character_id
from core_game.character.domain import PlayerCharacter, BaseCharacter
from core_game.character.schemas import (
    IdentityModel, PhysicalAttributesModel, PsychologicalAttributesModel, KnowledgeModel
)
from core_game.map.domain import Scenario

class SimulatedGameState:
    """
    Class to handle the game state in a simulated environment where agents can interact it. 
    It is used to store and manipulate the game state during simulations. 
    So it doesnt modify the real game state directly.
    """
    def __init__(self, game_state: GameState):
        self._map = SimulatedMap(game_state.game_map)
        self._characters = SimulatedCharacters(game_state.characters)
        self._layers: List[SimulationLayer] = []

    #CONTROL DE VERSIONS

    def begin_layer(self):
        parent = self._layers[-1] if self._layers else None
        self._layers.append(SimulationLayer(parent=parent, base_state=self))

    def current_layer(self) -> Optional[SimulationLayer]:
        return self._layers[-1] if self._layers else None

    @property
    def base_map(self) -> SimulatedMap:
        return self._map
    
    @property
    def base_characters(self) -> SimulatedCharacters:
        return self._characters

    def modify_map(self) -> SimulatedMap:
        layer = self.current_layer()
        if layer:
            return layer.modify_map()
        return self._map

    def modify_characters(self) -> SimulatedCharacters:
        layer = self.current_layer()
        if layer:
            return layer.modify_characters()
        return self._characters
    
    @property
    def read_map(self) -> SimulatedMap:
        layer = self.current_layer()
        return layer.map if layer else self._map

    @property
    def read_characters(self) -> SimulatedCharacters:
        layer = self.current_layer()
        return layer.characters if layer else self._characters

    def commit(self):
        if not self._layers:
            raise RuntimeError("No simulation layer to commit.")
        
        layer = self._layers.pop()
        parent = self._layers[-1] if self._layers else None

        if layer.has_modified_map():
            if parent:
                parent.set_modified_map(layer.get_modified_map())
            else:
                self._map = layer.get_modified_map()
                self._sync_map_to_domain()

        if layer.has_modified_characters():
            if parent:
                parent.set_modified_characters(layer.get_modified_characters())
            else:
                self._characters = layer.get_modified_characters()
                self._sync_characters_to_domain()

    def _sync_map_to_domain(self):
        game_state = GameStateSingleton.get_instance()
        game_state.update_map(self._map.get_state())

    def _sync_characters_to_domain(self):
        game_state = GameStateSingleton.get_instance()
        game_state.update_characters(self._characters.get_state())

    def rollback(self):
        if not self._layers:
            raise RuntimeError("No active simulation layers to rollback.")

        self._layers.pop()

        if not self._layers:
            game_state = GameStateSingleton.get_instance()
            self._map = SimulatedMap(game_state.game_map)
            self._characters = SimulatedCharacters(game_state.characters)
            print("[SimulatedGameState] Rolled back to base domain state.")

    # ---- MAP METHODS ------

    #MODIFYING METHODS
    def create_scenario(self, *args, **kwargs):
        return self.modify_map().create_scenario(*args, **kwargs)

    def modify_scenario(self, *args, **kwargs):
        return self.modify_map().modify_scenario(*args, **kwargs)

    def create_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().create_bidirectional_connection(*args, **kwargs)

    def delete_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().delete_bidirectional_connection(*args, **kwargs)

    def modify_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().modify_bidirectional_connection(*args, **kwargs)
    
    # READ METHODS

    def find_scenario(self, scenario_id: str):
        return self.read_map.find_scenario(scenario_id)

    def get_connection(self, scenario_id: str, direction_from):
        return self.read_map.get_connection(scenario_id, direction_from)

    def get_scenario_count(self):
        return self.read_map.get_scenario_count()

    def get_cluster_summary(self, *args, **kwargs):
        return self.read_map.get_cluster_summary(*args, **kwargs)

    def get_summary_list(self):
        return self.read_map.get_summary_list()

    def find_scenarios_by_attribute(self, *args, **kwargs):
        return self.read_map.find_scenarios_by_attribute(*args, **kwargs)

    # ---- CHARACTERS METHODS ------

    #MODIFYING METHODS

    def create_npc(self, *args, **kwargs):
        return self.modify_characters().create_npc(*args, **kwargs)

    def modify_character_identity(self, *args, **kwargs):
        return self.modify_characters().modify_character_identity(*args, **kwargs)

    def modify_character_physical(self, *args, **kwargs):
        return self.modify_characters().modify_character_physical(*args, **kwargs)

    def modify_character_psychological(self, *args, **kwargs):
        return self.modify_characters().modify_character_psychological(*args, **kwargs)

    def modify_character_knowledge(self, *args, **kwargs):
        return self.modify_characters().modify_character_knowledge(*args, **kwargs)

    def modify_character_dynamic_state(self, *args, **kwargs):
        return self.modify_characters().modify_character_dynamic_state(*args, **kwargs)

    def modify_character_narrative(self, *args, **kwargs):
        return self.modify_characters().modify_character_narrative(*args, **kwargs)
    
    # READ METHODS

    def get_character(self, *args, **kwargs):
        return self.read_characters.get_character(*args, **kwargs)

    def get_player(self, *args, **kwargs):
        return self.read_characters.get_player(*args, **kwargs)

    def characters_count(self):
        return self.read_characters.characters_count()

    def filter_characters(self, *args, **kwargs):
        return self.read_characters.filter_characters(*args, **kwargs)

    def group_by_scenario(self, *args, **kwargs):
        return self.read_characters.group_by_scenario(*args, **kwargs)

    def get_initial_summary(self, *args, **kwargs):
        return self.read_characters.get_initial_summary(*args, **kwargs)

    # ---- MAP AND CHARACTER METHODS ----
    
    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = None
    ) -> Tuple[PlayerCharacter, Scenario]:

        if self.read_characters.has_player():
            raise ValueError("Player already exists.")

        knowledge = knowledge or KnowledgeModel()

        player_model = PlayerCharacterModel(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=scenario_id
        )

        player = PlayerCharacter(player_model)
        can_place, msg = self.read_map.can_place_player(player, scenario_id)
        if not can_place:
            rollback_character_id()
            raise ValueError(msg)
        
        final_player = self.modify_characters().create_player_instance(player_model)
        scenario = self.modify_map().place_player(player, scenario_id)

        return final_player, scenario
    
    def place_character(self, character_id: str, scenario_id: str) -> Tuple[BaseCharacter,Scenario]:
        character = self.read_characters.get_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        if character.present_in_scenario == scenario_id:
            raise ValueError(f"Character is already present in scenario with ID {scenario_id}")
        
        success, message = self.read_map.can_place_character(character,scenario_id)
        if not success:
            raise ValueError(message)
        
        character = self.modify_characters().place_character(character,scenario_id)
        scenario = self.modify_map().place_character(character,scenario_id)
        return character, scenario

    def delete_character(self, character_id: str) -> BaseCharacter:
        deleted_character = self.modify_characters().try_delete_character(character_id)
        if deleted_character.present_in_scenario:
            try:
                self.modify_map().try_remove_character_from_scenario(deleted_character, deleted_character.present_in_scenario)
            except Exception as e:
                return deleted_character
        return deleted_character
    
    def remove_character_from_scenario(self, character_id: str) -> Tuple[BaseCharacter,Scenario]:
        character, scenario_id = self.modify_characters().try_remove_character_from_scenario(character_id)
        scenario = self.modify_map().try_remove_character_from_scenario(character, scenario_id)
        return character, scenario

    def delete_scenario(self, scenario_id: str) -> Scenario:
        self.modify_characters().try_remove_any_characters_at_scenario(scenario_id)
        return self.modify_map().delete_scenario(scenario_id)
        
    
class SimulatedGameStateSingleton:
    """ Singleton class to manage the simulated game state.
    This class ensures that only one instance of SimulatedGameState exists at any time."""
    _instance: SimulatedGameState | None = None

    @classmethod
    def get_instance(cls): 
        """
        Returns the singleton instance of SimulatedGameState.
        If it doesn't exist, it creates a new one.
        """
        if cls._instance is None:
            cls._instance = SimulatedGameState(GameStateSingleton.get_instance())
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Resets the singleton instance of SimulatedGameState.
        This is useful for starting a new simulation without interference from previous states.
        """
        cls._instance = SimulatedGameState(GameStateSingleton.get_instance())