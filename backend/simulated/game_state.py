
from simulated.components.map import SimulatedMap
from simulated.components.characters import SimulatedCharacters
from simulated.versioning.layer import SimulationLayer
from typing import List, Tuple, Optional
from core_game.character.schemas import PlayerCharacterModel, rollback_character_id
from core_game.character.domain import PlayerCharacter, BaseCharacter
from core_game.character.schemas import (
    IdentityModel, PhysicalAttributesModel, PsychologicalAttributesModel, KnowledgeModel
)
from core_game.map.domain import Scenario
from simulated.versioning.manager import GameStateVersionManager

class SimulatedGameState:
    """
    Acts as a Facade to interact with the game state.
    It delegates state access (read/write) to a Version Manager.
    It does NOT handle versioning logic itself.
    """
    def __init__(self, version_manager: GameStateVersionManager):
        self._version_manager = version_manager

    # --- Propiedades de ayuda para acceder al estado actual ---
    @property
    def _read_map(self) -> SimulatedMap:
        return self._version_manager.get_current_map(for_writing=False)

    @property
    def _write_map(self) -> SimulatedMap:
        return self._version_manager.get_current_map(for_writing=True)

    @property
    def _read_characters(self) -> SimulatedCharacters:
        return self._version_manager.get_current_characters(for_writing=False)

    @property
    def _write_characters(self) -> SimulatedCharacters:
        return self._version_manager.get_current_characters(for_writing=True)

    # ---- MAP METHODS ------

    #MODIFYING METHODS
    def create_scenario(self, *args, **kwargs):
        return self._write_map.create_scenario(*args, **kwargs)

    def modify_scenario(self, *args, **kwargs):
        return self._write_map.modify_scenario(*args, **kwargs)

    def create_bidirectional_connection(self, *args, **kwargs):
        return self._write_map.create_bidirectional_connection(*args, **kwargs)

    def delete_bidirectional_connection(self, *args, **kwargs):
        return self._write_map.delete_bidirectional_connection(*args, **kwargs)

    def modify_bidirectional_connection(self, *args, **kwargs):
        return self._write_map.modify_bidirectional_connection(*args, **kwargs)
    
    # READ METHODS

    def find_scenario(self, scenario_id: str):
        return self._read_map.find_scenario(scenario_id)

    def get_connection(self, scenario_id: str, direction_from):
        return self._read_map.get_connection(scenario_id, direction_from)

    def get_scenario_count(self):
        return self._read_map.get_scenario_count()

    def get_map_cluster_summary(self, *args, **kwargs):
        return self._read_map.get_cluster_summary(*args, **kwargs)

    def get_map_summary_list(self):
        return self._read_map.get_summary_list()

    def find_scenarios_by_attribute(self, *args, **kwargs):
        return self._read_map.find_scenarios_by_attribute(*args, **kwargs)

    # ---- CHARACTERS METHODS ------

    #MODIFYING METHODS

    def create_npc(self, *args, **kwargs):
        return self._write_characters.create_npc(*args, **kwargs)

    def modify_character_identity(self, *args, **kwargs):
        return self._write_characters.modify_character_identity(*args, **kwargs)

    def modify_character_physical(self, *args, **kwargs):
        return self._write_characters.modify_character_physical(*args, **kwargs)

    def modify_character_psychological(self, *args, **kwargs):
        return self._write_characters.modify_character_psychological(*args, **kwargs)

    def modify_character_knowledge(self, *args, **kwargs):
        return self._write_characters.modify_character_knowledge(*args, **kwargs)

    def modify_character_dynamic_state(self, *args, **kwargs):
        return self._write_characters.modify_character_dynamic_state(*args, **kwargs)

    def modify_character_narrative(self, *args, **kwargs):
        return self._write_characters.modify_character_narrative(*args, **kwargs)
    
    # READ METHODS

    def get_character(self, *args, **kwargs):
        return self._read_characters.get_character(*args, **kwargs)

    def get_player(self, *args, **kwargs):
        return self._read_characters.get_player(*args, **kwargs)

    def characters_count(self):
        return self._read_characters.characters_count()

    def filter_characters(self, *args, **kwargs):
        return self._read_characters.filter_characters(*args, **kwargs)

    def group_by_scenario(self, *args, **kwargs):
        return self._read_characters.group_by_scenario(*args, **kwargs)

    def get_initial_characters_summary(self, *args, **kwargs):
        return self._read_characters.get_initial_summary(*args, **kwargs)

    # ---- MAP AND CHARACTER METHODS ----
    
    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = None
    ) -> Tuple[PlayerCharacter, Scenario]:

        if self._read_characters.has_player():
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
        can_place, msg = self._read_map.can_place_player(player, scenario_id)
        if not can_place:
            rollback_character_id()
            raise ValueError(msg)
        
        final_player = self._write_characters.create_player_instance(player_model)
        scenario = self._write_map.place_player(player, scenario_id)

        return final_player, scenario
    
    def place_character(self, character_id: str, scenario_id: str) -> Tuple[BaseCharacter,Scenario]:
        character = self._read_characters.get_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        if character.present_in_scenario == scenario_id:
            raise ValueError(f"Character is already present in scenario with ID {scenario_id}")
        
        success, message = self._read_map.can_place_character(character,scenario_id)
        if not success:
            raise ValueError(message)
        
        character = self._write_characters.place_character(character,scenario_id)
        scenario = self._write_map.place_character(character,scenario_id)
        return character, scenario

    def delete_character(self, character_id: str) -> BaseCharacter:
        deleted_character = self._write_characters.try_delete_character(character_id)
        if deleted_character.present_in_scenario:
            try:
                self._write_map.try_remove_character_from_scenario(deleted_character, deleted_character.present_in_scenario)
            except Exception as e:
                return deleted_character
        return deleted_character
    
    def remove_character_from_scenario(self, character_id: str) -> Tuple[BaseCharacter,Scenario]:
        character, scenario_id = self._write_characters.try_remove_character_from_scenario(character_id)
        scenario = self._write_map.try_remove_character_from_scenario(character, scenario_id)
        return character, scenario

    def delete_scenario(self, scenario_id: str) -> Scenario:
        self._write_characters.try_remove_any_characters_at_scenario(scenario_id)
        return self._write_map.delete_scenario(scenario_id)
        