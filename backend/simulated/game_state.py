
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
from simulated.versioning.layers.manager import GameStateVersionManager
from core_game.game_event.constants import EVENT_STATUS_LITERAL
from core_game.game_event.activation_conditions.schemas import *
from core_game.game_event.domain import (
    BaseGameEvent
)
from core_game.game_event.schemas import *
from core_game.exceptions import PlayerDeletionError
import random

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
        # TODO
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

    def place_character_main_cluster_random_safe_scenario(self, character_id: str) -> Tuple[BaseCharacter, Scenario]:
        """
        Finds a random, safe scenario within the largest cluster and places the character there.

        This method identifies the main connected component of the map, shuffles its
        scenarios, and iterates through them to find the first one where the
        character can be safely placed.

        Args:
            character_id: The ID of the character to place.

        Returns:
            A tuple containing the updated character object and the scenario where it was placed.

        Raises:
            KeyError: If the character_id does not exist.
            ValueErro: If the map has no scenarios or clusters.
            ValueError: If no suitable scenario is found in the main cluster after checking all options.
        """
        print(f"--- Attempting to safely place character '{character_id}' in a random scenario of the main cluster ---")
        
        # 1. Get the character to be placed
        character = self.read_only_characters.get_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")

        # 2. Find the main cluster
        main_cluster_ids = self.read_only_map.get_main_cluster()
        if not main_cluster_ids:
            raise ValueError("Cannot place character: The map has no scenarios or clusters.")
        
        # 3. Shuffle scenarios for randomness
        shuffled_scenario_ids = list(main_cluster_ids)
        random.shuffle(shuffled_scenario_ids)

        # 4. Find a safe scenario and place the character
        for scenario_id in shuffled_scenario_ids:
            print(f"  - Checking scenario '{scenario_id}' for placement...")
            if isinstance(character, PlayerCharacter):
                can_place, message = self.read_only_map.can_place_player(character, scenario_id)
            else:
                can_place, message = self.read_only_map.can_place_character(character, scenario_id)
            
            if can_place:
                print(f"    - ✅ Safe to place. Placing character '{character_id}' in scenario '{scenario_id}'.")

                return self.place_character(character_id, scenario_id)
            else:
                print(f"    - ❌ Cannot place here. Reason: {message}")

        raise ValueError(f"Could not find a safe scenario to place character '{character_id}' in the main cluster.")


    def delete_character(self, character_id: str) -> BaseCharacter:
        # TODO
        # Consider moving to a dedicated service if used elsewhere.
        deleted_character = self.characters.try_delete_character(character_id)
        if deleted_character.present_in_scenario:
            try:
                self.map.try_remove_character_from_scenario(deleted_character, deleted_character.present_in_scenario)
            except Exception as e:
                return deleted_character
        return deleted_character
    
    def remove_character_from_scenario(self, character_id: str) -> Tuple[BaseCharacter,Scenario]:
        # TODO
        # Consider moving to a dedicated service if used elsewhere.
        character, scenario_id = self.characters.try_remove_character_from_scenario(character_id)
        scenario = self.map.try_remove_character_from_scenario(character, scenario_id)
        return character, scenario

    def delete_scenario(self, scenario_id: str) -> Scenario:
        # TODO
        # Consider moving to a dedicated service if used elsewhere.
        scenario = self.read_only_map.find_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario with ID '{scenario_id}' does not exist.")
        self.characters.try_remove_any_characters_at_scenario(scenario_id)
        return self.map.delete_scenario(scenario_id)
    
    # GAME EVENT METHODS

    def _validate_activation_conditions(self, conditions: List[ActivationConditionModel]):
        """
        Private helper to validate a list of activation conditions against the game state.
        This centralized method is reused by any operation that adds or links conditions.
        """
        if not conditions:
            raise ValueError("At least one activation condition is required.")

        for condition in conditions:
            if isinstance(condition, AreaEntryConditionModel):
                if not self.read_only_map.find_scenario(condition.scenario_id):
                    raise ValueError(f"Activation condition 'area_entry' refers to a non-existent scenario_id '{condition.scenario_id}'.")
            
            elif isinstance(condition, EventCompletionConditionModel):
                if not self.read_only_events.find_event(condition.source_event_id):
                    raise ValueError(f"Activation condition 'event_completion' refers to a non-existent source_event_id '{condition.source_event_id}'.")

            elif isinstance(condition, CharacterInteractionOptionModel):
                if not self.read_only_characters.get_character(condition.character_id):
                    raise ValueError(f"Activation condition 'character_interaction' refers to a non-existent character_id '{condition.character_id}'.")


    def create_available_npc_conversation(
        self,
        title: str,
        description: str,
        npc_ids: List[str],
        activation_conditions: List[ActivationConditionModel],
        source_beat_id: Optional[str]
    ) -> BaseGameEvent:
        """
        Orchestrates the creation of an NPC conversation event.

        It performs all cross-component validation before committing the
        event to the event system.
        """
        if not npc_ids:
            raise ValueError(f"At least one npc is required for this event.")
        player = self.read_only_characters.get_player()
        player_id = player.id if player else None
        unique_npc_ids = set(npc_ids)
        for npc_id in unique_npc_ids:
            if not self.read_only_characters.get_character(npc_id):
                raise ValueError(f"Character with ID '{npc_id}' not found.")
            if player_id == npc_id:
                raise ValueError(f"Character with ID '{npc_id}' is a player. This event CANNOT have a player involved.")

        
        if source_beat_id and not self.read_only_narrative.get_beat(source_beat_id):
            raise ValueError(f"Source beat with ID '{source_beat_id}' not found.")

        self._validate_activation_conditions(activation_conditions)

        event_model = NPCConversationEventModel(
            title=title,
            description=description,
            npc_ids=list(unique_npc_ids),
            source_beat_id=source_beat_id,
            activation_conditions=activation_conditions,
            status="AVAILABLE"  # Se vuelve disponible inmediatamente porque tiene triggers.
        )

        created_event = self.events.add_event(event_model)
        
        return created_event
    
    def create_available_player_npc_conversation(
        self,
        title: str,
        description: str,
        npc_ids: List[str],
        activation_conditions: List[ActivationConditionModel],
        source_beat_id: Optional[str]
    ) -> BaseGameEvent:
        """
        Orchestrates the creation of a Player-NPC conversation event.
        Performs all cross-component validation before creating the event.
        """
        player = self.read_only_characters.get_player()
        if not player:
            raise ValueError("A player character must exist to create a player-involved conversation.")
        filtered_npc_ids = set([npc_id for npc_id in npc_ids if npc_id != player.id])
        if not filtered_npc_ids:
            raise ValueError("At least one NPC is required for a player-npc conversation.")
            
        for npc_id in filtered_npc_ids:
            if not self.read_only_characters.get_character(npc_id):
                raise ValueError(f"Character with ID '{npc_id}' not found.")
        
        if source_beat_id and not self.read_only_narrative.get_beat(source_beat_id):
            raise ValueError(f"Source beat with ID '{source_beat_id}' not found.")

        self._validate_activation_conditions(activation_conditions)

        event_model = PlayerNPCConversationEventModel(
            title=title,
            description=description,
            npc_ids=list(filtered_npc_ids),
            source_beat_id=source_beat_id,
            activation_conditions=activation_conditions,
            status="AVAILABLE"
        )

        created_event = self.events.add_event(event_model)
        return created_event

    def create_available_cutscene(
        self,
        title: str,
        description: str,
        activation_conditions: List[ActivationConditionModel],
        source_beat_id: Optional[str],
        involved_character_ids: Optional[List[str]],
        involved_scenario_ids: Optional[List[str]]
    ) -> BaseGameEvent:
        """
        Orchestrates the creation of a Cutscene event.
        Performs all cross-component validation before creating the event.
        """
        if source_beat_id and not self.read_only_narrative.get_beat(source_beat_id):
            raise ValueError(f"Source beat with ID '{source_beat_id}' not found.")

        self._validate_activation_conditions(activation_conditions)

        unique_character_ids = set(involved_character_ids) if involved_character_ids else set()
        unique_scenario_ids = set(involved_scenario_ids) if involved_scenario_ids else set()

        for char_id in unique_character_ids:
            if not self.read_only_characters.get_character(char_id):
                raise ValueError(f"Involved character with ID '{char_id}' not found.")

        for scenario_id in unique_scenario_ids:
            if not self.read_only_map.find_scenario(scenario_id):
                raise ValueError(f"Involved scenario with ID '{scenario_id}' not found.")

        
        final_char_ids = list(unique_character_ids)
        final_scenario_ids = list(unique_scenario_ids)

        event_model = CutsceneEventModel(
            title=title,
            description=description,
            source_beat_id=source_beat_id,
            activation_conditions=activation_conditions,
            status="AVAILABLE",
            involved_character_ids=final_char_ids,
            involved_scenario_ids=final_scenario_ids
        )
        created_event = self.events.add_event(event_model)
        return created_event


    def create_available_narrator_intervention(
        self,
        title: str,
        description: str,
        activation_conditions: List[ActivationConditionModel],
        source_beat_id: Optional[str]
    ) -> BaseGameEvent:
        """
        Orchestrates the creation of a Narrator Intervention event.
        Performs all cross-component validation before creating the event.
        """
        
        if source_beat_id and not self.read_only_narrative.get_beat(source_beat_id):
            raise ValueError(f"Source beat with ID '{source_beat_id}' not found.")

        self._validate_activation_conditions(activation_conditions)

        event_model = NarratorInterventionEventModel(
            title=title,
            description=description,
            source_beat_id=source_beat_id,
            activation_conditions=activation_conditions,
            status="AVAILABLE"
        )

        created_event = self.events.add_event(event_model)
        return created_event

    def link_conditions_to_event(self, event_id: str, conditions: List[ActivationConditionModel]):
        """
        Orchestrates linking new activation conditions to an existing event.
        """
        
        event = self.read_only_events.find_event(event_id)
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
            
        if event.status in ["RUNNING", "COMPLETED"]:
            raise ValueError(f"Cannot link new conditions to event '{event_id}'. It is already in '{event.status}' status.")
        

        self._validate_activation_conditions(conditions)

        self.events.link_conditions_to_event(event_id, conditions)

    def prune_scenarios_outside_main_cluster(self) -> bool:
        """Prunes all scenarios not forming part of main cluster. Returns False if any went wrong while doing"""
        outside_clusters = self.read_only_map.get_outside_clusters()
        for cluster in outside_clusters:
            for scenario_id in cluster:
                try:
                    scenario = self.read_only_map.find_scenario(scenario_id)
                    assert scenario is not None
                    for character_id in scenario.present_characters_ids:
                        self.place_character_main_cluster_random_safe_scenario(character_id)
                    self.delete_scenario(scenario_id)
                except Exception as e:
                    return False
        return True

