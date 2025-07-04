
from simulated.components.map import SimulatedMap
from simulated.components.characters import SimulatedCharacters
from simulated.components.game_session import SimulatedGameSession
from simulated.components.relationships import SimulatedRelationships
from simulated.components.narrative import SimulatedNarrative
from typing import List, Tuple, Optional, Any, Set
from core_game.character.schemas import PlayerCharacterModel, rollback_character_id
from simulated.components.game_events import SimulatedGameEvents
from core_game.character.domain import PlayerCharacter, BaseCharacter
from core_game.character.schemas import (
    IdentityModel, PhysicalAttributesModel, PsychologicalAttributesModel, KnowledgeModel
)
from core_game.map.domain import Scenario
from core_game.narrative.schemas import (
    NarrativeBeatModel,
    FailureConditionModel,
    RiskTriggeredBeat,
    NarrativeStructureTypeModel
)
from simulated.versioning.manager import GameStateVersionManager
from core_game.game_event.constants import EVENT_STATUS_LITERAL
from core_game.game_event.domain import (
    BaseGameEvent
)

class SimulatedGameState:
    """
    Acts as a Facade to interact with the game state.
    It delegates state access (read/write) to a Version Manager.
    It does NOT handle versioning logic itself.
    """
    def __init__(self, version_manager: GameStateVersionManager):
        self._version_manager = version_manager
    
    # --- Map Accessors ---
    @property
    def map(self) -> SimulatedMap:
        """
        [WRITE ACCESS] Returns the write-enabled map component.
        Accessing this may trigger a copy-on-write for the current transaction.
        Use for any operation that MODIFIES the map state.
        """
        return self._version_manager.get_current_map(for_writing=True)

    @property
    def read_only_map(self) -> SimulatedMap:
        """
        [READ-ONLY ACCESS] Returns the read-only map component.
        Guaranteed to be fast and not perform a copy. Use for all
        operations that ONLY READ from the map state.
        """
        return self._version_manager.get_current_map(for_writing=False)

    # --- Characters Accessors ---
    @property
    def characters(self) -> SimulatedCharacters:
        """
        [WRITE ACCESS] Returns the write-enabled characters component.
        """
        return self._version_manager.get_current_characters(for_writing=True)

    @property
    def read_only_characters(self) -> SimulatedCharacters:
        """
        [READ-ONLY ACCESS] Returns the read-only characters component.
        """
        return self._version_manager.get_current_characters(for_writing=False)

    # --- Relationships Accessors ---
    @property
    def relationships(self) -> SimulatedRelationships:
        """
        [WRITE ACCESS] Returns the write-enabled relationships component.
        """
        return self._version_manager.get_current_relationships(for_writing=True)

    @property
    def read_only_relationships(self) -> SimulatedRelationships:
        """
        [READ-ONLY ACCESS] Returns the read-only relationships component.
        """
        return self._version_manager.get_current_relationships(for_writing=False)

    # --- Narrative Accessors ---
    @property
    def narrative(self) -> SimulatedNarrative:
        """
        [WRITE ACCESS] Returns the write-enabled narrative component.
        """
        return self._version_manager.get_current_narrative(for_writing=True)

    @property
    def read_only_narrative(self) -> SimulatedNarrative:
        """
        [READ-ONLY ACCESS] Returns the read-only narrative component.
        """
        return self._version_manager.get_current_narrative(for_writing=False)
        
    # --- Game Events Accessors ---
    @property
    def events(self) -> SimulatedGameEvents:
        """
        [WRITE ACCESS] Returns the write-enabled game events component.
        """
        return self._version_manager.get_current_game_events(for_writing=True)

    @property
    def read_only_events(self) -> SimulatedGameEvents:
        """
        [READ-ONLY ACCESS] Returns the read-only game events component.
        """
        return self._version_manager.get_current_game_events(for_writing=False)

    # --- Session Accessors ---
    @property
    def session(self) -> SimulatedGameSession:
        """
        [WRITE ACCESS] Returns the write-enabled session component.
        """
        return self._version_manager.get_current_session(for_writing=True)

    @property
    def read_only_session(self) -> SimulatedGameSession:
        """
        [READ-ONLY ACCESS] Returns the read-only session component.
        """
        return self._version_manager.get_current_session(for_writing=False)
    
    # ---- MAP AND CHARACTER METHODS ----
    
    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = None
    ) -> Tuple[PlayerCharacter, Scenario]:
        # TODO: This logic coordinates multiple components.
        # Consider moving to a dedicated service if used elsewhere.
        if self.read_only_characters.has_player():
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
        can_place, msg = self.read_only_map.can_place_player(player, scenario_id)
        if not can_place:
            rollback_character_id()
            raise ValueError(msg)
        
        final_player = self.characters.create_player_instance(player_model)
        scenario = self.map.place_player(player, scenario_id)

        return final_player, scenario
    
    def place_character(self, character_id: str, scenario_id: str) -> Tuple[BaseCharacter,Scenario]:
        # TODO: This logic coordinates multiple components.
        # Consider moving to a dedicated service if used elsewhere.
        character = self.read_only_characters.get_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        if character.present_in_scenario == scenario_id:
            raise ValueError(f"Character is already present in scenario with ID {scenario_id}")
        
        success, message = self.read_only_map.can_place_character(character,scenario_id)
        if not success:
            raise ValueError(message)
        
        character = self.characters.place_character(character,scenario_id)
        scenario = self.map.place_character(character,scenario_id)
        return character, scenario

    def delete_character(self, character_id: str) -> BaseCharacter:
        # TODO: This logic coordinates multiple components.
        # Consider moving to a dedicated service if used elsewhere.
        deleted_character = self.characters.try_delete_character(character_id)
        if deleted_character.present_in_scenario:
            try:
                self.map.try_remove_character_from_scenario(deleted_character, deleted_character.present_in_scenario)
            except Exception as e:
                return deleted_character
        return deleted_character
    
    def remove_character_from_scenario(self, character_id: str) -> Tuple[BaseCharacter,Scenario]:
        # TODO: This logic coordinates multiple components.
        # Consider moving to a dedicated service if used elsewhere.
        character, scenario_id = self.characters.try_remove_character_from_scenario(character_id)
        scenario = self.map.try_remove_character_from_scenario(character, scenario_id)
        return character, scenario

    def delete_scenario(self, scenario_id: str) -> Scenario:
        # TODO: This logic coordinates multiple components.
        # Consider moving to a dedicated service if used elsewhere.
        self.characters.try_remove_any_characters_at_scenario(scenario_id)
        return self.map.delete_scenario(scenario_id)
        