
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

    # ---- MAP METHODS ------

    #MODIFYING METHODS
    def create_scenario(self, *args, **kwargs):
        return self.map.create_scenario(*args, **kwargs)

    def modify_scenario(self, *args, **kwargs):
        return self.map.modify_scenario(*args, **kwargs)

    def create_bidirectional_connection(self, *args, **kwargs):
        return self.map.create_bidirectional_connection(*args, **kwargs)

    def delete_bidirectional_connection(self, *args, **kwargs):
        return self.map.delete_bidirectional_connection(*args, **kwargs)

    def modify_bidirectional_connection(self, *args, **kwargs):
        return self.map.modify_bidirectional_connection(*args, **kwargs)
    
    # READ METHODS

    def find_scenario(self, scenario_id: str):
        return self.read_only_map.find_scenario(scenario_id)

    def get_connection(self, scenario_id: str, direction_from):
        return self.read_only_map.get_connection(scenario_id, direction_from)

    def get_scenario_count(self):
        return self.read_only_map.get_scenario_count()

    def get_map_cluster_summary(self, *args, **kwargs):
        return self.read_only_map.get_cluster_summary(*args, **kwargs)

    def get_map_summary_list(self):
        return self.read_only_map.get_summary_list()

    def find_scenarios_by_attribute(self, *args, **kwargs):
        return self.read_only_map.find_scenarios_by_attribute(*args, **kwargs)

    # ---- CHARACTERS METHODS ------

    #MODIFYING METHODS

    def create_npc(self, *args, **kwargs):
        return self.characters.create_npc(*args, **kwargs)

    def modify_character_identity(self, *args, **kwargs):
        return self.characters.modify_character_identity(*args, **kwargs)

    def modify_character_physical(self, *args, **kwargs):
        return self.characters.modify_character_physical(*args, **kwargs)

    def modify_character_psychological(self, *args, **kwargs):
        return self.characters.modify_character_psychological(*args, **kwargs)

    def modify_character_knowledge(self, *args, **kwargs):
        return self.characters.modify_character_knowledge(*args, **kwargs)

    def modify_character_dynamic_state(self, *args, **kwargs):
        return self.characters.modify_character_dynamic_state(*args, **kwargs)

    def modify_character_narrative(self, *args, **kwargs):
        return self.characters.modify_character_narrative(*args, **kwargs)
    
    # READ METHODS

    def get_character(self, *args, **kwargs):
        return self.read_only_characters.get_character(*args, **kwargs)

    def get_player(self, *args, **kwargs):
        return self.read_only_characters.get_player(*args, **kwargs)

    def characters_count(self):
        return self.read_only_characters.characters_count()

    def filter_characters(self, *args, **kwargs):
        return self.read_only_characters.filter_characters(*args, **kwargs)

    def group_by_scenario(self, *args, **kwargs):
        return self.read_only_characters.group_by_scenario(*args, **kwargs)

    def get_initial_characters_summary(self, *args, **kwargs):
        return self.read_only_characters.get_initial_summary(*args, **kwargs)

    # ---- RELATIONSHIPS METHODS ----

    # MODIFYING METHODS
    def create_relationship_type(self, *args, **kwargs):
        return self.relationships.create_relationship_type(*args, **kwargs)

    def create_directed_relationship(self, *args, **kwargs):
        return self.relationships.create_directed_relationship(*args, **kwargs)

    def create_undirected_relationship(self, *args, **kwargs):
        return self.relationships.create_undirected_relationship(*args, **kwargs)

    def modify_relationship_intensity(self, *args, **kwargs):
        return self.relationships.modify_relationship_intensity(*args, **kwargs)

    # READ METHODS
    def get_relationship_details(self, *args, **kwargs):
        return self.read_only_relationships.get_relationship_details(*args, **kwargs)

    def get_relationship_count(self) -> int:
        return self.read_only_relationships.relationship_count()

    def get_initial_relationships_summary(self) -> str:
        return self.read_only_relationships.get_initial_summary()

    # ---- SESSION METHODS ----
    def set_user_prompt(self, prompt: str) -> None:
        self.session.set_user_prompt(prompt)

    def set_refined_prompt(self, prompt: str) -> None:
        self.session.set_refined_prompt(prompt)

    def set_main_goal(self, goal: str) -> None:
        self.narrative.set_main_goal(goal)

    def set_global_flag(self, key: str, value: Any) -> None:
        self.session.set_global_flag(key, value)

    def remove_global_flag(self, key: str) -> None:
        self.session.remove_global_flag(key)

    def advance_time(self, minutes: int) -> None:
        self.session.advance_time(minutes)

    def get_user_prompt(self):
        return self.read_only_session.get_user_prompt()

    def get_refined_prompt(self):
        return self.read_only_session.get_refined_prompt()

    def get_main_goal(self):
        return self.read_only_narrative.get_main_goal()

    def get_global_flags(self):
        return self.read_only_session.get_global_flags()

    def get_time(self):
        return self.read_only_session.get_time()

    # ---- NARRATIVE METHODS ----
    def get_initial_narrative_summary(self) -> str:
        return self.read_only_narrative.get_initial_summary()
    
    def set_narrative_structure(self, structure_type: NarrativeStructureTypeModel) -> None:
        self.narrative.set_narrative_structure(structure_type)

    def get_current_stage_index(self) -> int:
        """Return the index of the currently active narrative stage."""
        return self.read_only_narrative.get_current_stage_index()

    def get_next_stage_index(self) -> int:
        """Return the index of the next narrative stage if available."""
        return self.read_only_narrative.get_next_stage_index()

    def add_narrative_beat(self, stage_index: int, beat: NarrativeBeatModel) -> None:
        self.narrative.add_narrative_beat(stage_index, beat)

    def add_failure_condition(self, failure_condition: FailureConditionModel) -> None:
        self.narrative.add_failure_condition(failure_condition)

    def add_risk_triggered_beats(self, condition_id: str, risk_triggered: RiskTriggeredBeat) -> None:
        self.narrative.add_risk_triggered_beats(condition_id, risk_triggered)

    def set_failure_risk_level(self, condition_id: str, risk_level: int) -> None:
        self.narrative.set_failure_risk_level(condition_id, risk_level)

    def get_stage_beats(self, stage_index: int):
        """Return beats for a given stage index."""
        return self.read_only_narrative.get_stage_beats(stage_index)

    def get_current_stage_beats(self):
        """Return beats of the current narrative stage."""
        index = self.get_current_stage_index()
        return self.get_stage_beats(index)

    def get_next_stage_beats(self):
        """Return beats of the next narrative stage if available."""
        index = self.get_next_stage_index()
        return self.get_stage_beats(index)

    def narrative_beats_count(self) -> int:
        """Return the total number of beats tracked in the narrative."""
        count = 0
        structure = self.read_only_narrative.get_state().narrative_structure
        if structure:
            for stage in structure.stages:
                count += len(stage.stage_beats)
        for fc in self.read_only_narrative.get_state().failure_conditions:
            count+= len(fc.risk_triggered_beats)

        return count

    def get_narrative_beat(self, beat_id: str) -> NarrativeBeatModel | None:
        """Return a beat by its id from any source."""
        return self.read_only_narrative.get_beat(beat_id)

    def get_failure_condition(self, condition_id: str) -> FailureConditionModel | None:
        """Return a failure condition by id if it exists."""
        return self.read_only_narrative.get_failure_condition(condition_id)

    def list_active_beats(self) -> List[NarrativeBeatModel]:
        return self.read_only_narrative.list_active_beats()

    def list_pending_beats_main(self) -> List[NarrativeBeatModel]:
        return self.read_only_narrative.list_pending_beats_main()


    # ---- GAME EVENTS METHODS ----
    def get_initial_events_summary(self) -> str:
        return self.read_only_events.get_initial_summary()
    
    def get_current_running_event(self) -> Optional[BaseGameEvent]:
        return self.read_only_events.get_current_running_event()

    def get_completed_event_ids(self) -> Set[str]:
        return self.read_only_events.get_completed_event_ids()


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
        