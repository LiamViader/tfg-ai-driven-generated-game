from copy import deepcopy
from typing import Optional, Dict, Set, Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from simulated.game_state import SimulatedGameState



from core_game.character.domain import Characters, BaseCharacter, PlayerCharacter, NPCCharacter
from core_game.character.schemas import PlayerCharacterModel, rollback_character_id, NonPlayerCharacterModel, NarrativeImportance, NarrativeRole, NarrativePurposeModel
from core_game.character.constants import Gender
from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    KnowledgeModel,
    DynamicStateModel,
)
from core_game.map.domain import Scenario

class SimulatedCharacters:
    """Lightweight wrapper around :class:`Characters` for isolated modifications."""

    def __init__(self, characters: Characters, simulated_game_state: 'SimulatedGameState') -> None:
        self._original_state: Characters = characters
        self._copied_state: Optional[Characters] = None
        self._working_state: Characters = self._original_state
        self._simulated_game_state: 'SimulatedGameState' = simulated_game_state
        self._is_modified: bool = False
        self._deleted_characters: Dict[str, BaseCharacter] = {}
        self._added_characters: Set[str] = set()
        self._modified_characters: Set[str] = set()

    @property
    def working_state(self) -> Characters:
        return self._working_state

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _started_modifying(self) -> None:
        if not self._is_modified:
            self._copied_state = Characters(self._original_state.to_model())
            self._working_state = self._copied_state
            self._is_modified = True

    # ------------------------------------------------------------------
    # Proxy methods
    # ------------------------------------------------------------------

    def create_npc(
        self, 
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        narrative: NarrativeWeightModel,
        knowledge: KnowledgeModel,
        dynamic_state: DynamicStateModel = DynamicStateModel()
    ) -> NPCCharacter:
        
        self._started_modifying()

        knowledge = knowledge or KnowledgeModel()
        dynamic_state = dynamic_state or DynamicStateModel()

        npc_model = NonPlayerCharacterModel(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=None,
            dynamic_state=dynamic_state,
            narrative=narrative,
        )
        npc = NPCCharacter(npc_model)

        #aqui anirien comprovacions i en cas de fallada es faria rollback del id i es retornaria error.

        self._working_state.add_npc(npc)

        self._added_characters.add(npc.id)
        return npc

    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = KnowledgeModel()
    ) -> Tuple[PlayerCharacter, Scenario]:

        if self.working_state.has_player():
            raise ValueError("Player already exists")

        knowledge = knowledge or KnowledgeModel()

        player_model = PlayerCharacterModel(
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=scenario_id
        )

        player = PlayerCharacter(player_model)

        success, message = self._simulated_game_state.simulated_map.can_place_player(player,scenario_id)
        if not success:
            rollback_character_id()
            raise ValueError(message)
        
        self._started_modifying()
        scenario = self._simulated_game_state.simulated_map.place_player(player,scenario_id)
        player = self.working_state.add_player(player)
        self._added_characters.add(player.id)

        return player, scenario

    def modify_character_identity(
        self, 
        character_id: str,
        new_full_name: Optional[str] = None,
        new_alias: Optional[str] = None,
        new_age: Optional[int] = None,
        new_gender: Optional[Gender] = None,
        new_profession: Optional[str] = None,
        new_species: Optional[str] = None,
        new_alignment: Optional[str] = None,
    ) -> None:
        if not self.working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._started_modifying()
        self.working_state.modify_character_identity(
            character_id=character_id,
            new_full_name=new_full_name,
            new_alias=new_alias,
            new_age=new_age,
            new_gender=new_gender,
            new_profession=new_profession,
            new_species=new_species,
            new_alignment=new_alignment
        )
        
        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def modify_character_physical(
        self,
        character_id: str,
        new_appearance: Optional[str] = None,
        new_distinctive_features: Optional[list] = None,
        append_distinctive_features: bool = False,
        new_clothing_style: Optional[str] = None,
        new_characteristic_items: Optional[list] = None,
        append_characteristic_items: bool = False
    ) -> None:
        
        if not self.working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._started_modifying()
        self.working_state.modify_character_physical(
            character_id=character_id,
            new_appearance=new_appearance,
            new_distinctive_features=new_distinctive_features,
            append_distinctive_features=append_distinctive_features,
            new_clothing_style=new_clothing_style,
            new_characteristic_items=new_characteristic_items,
            append_characteristic_items=append_characteristic_items,
        )
        
        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def modify_character_psychological(
        self,
        character_id: str,
        new_personality_summary: Optional[str] = None,
        new_personality_tags: Optional[List[str]] = None,
        append_personality_tags: bool = False,
        new_motivations: Optional[List[str]] = None,
        append_motivations: bool = False,
        new_values: Optional[List[str]] = None,
        append_values: bool = False,
        new_fears_and_weaknesses: Optional[List[str]] = None,
        append_fears_and_weaknesses: bool = False,
        new_communication_style: Optional[str] = None,
        new_backstory: Optional[str] = None,
        new_quirks: Optional[List[str]] = None,
        append_quirks: bool = False
    ) -> None:
        if not self.working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        self._started_modifying()
        self.working_state.modify_character_psychological(
            character_id=character_id,
            new_personality_summary=new_personality_summary,
            new_personality_tags=new_personality_tags,
            append_personality_tags=append_personality_tags,
            new_motivations=new_motivations,
            append_motivations=append_motivations,
            new_values=new_values,
            append_values=append_values,
            new_fears_and_weaknesses=new_fears_and_weaknesses,
            append_fears_and_weaknesses=append_fears_and_weaknesses,
            new_communication_style=new_communication_style,
            new_backstory=new_backstory,
            new_quirks=new_quirks,
            append_quirks=append_quirks
        )

        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def modify_character_knowledge(
        self,
        character_id: str,
        new_background_knowledge: Optional[List[str]] = None,
        append_background_knowledge: bool = False,
        new_acquired_knowledge: Optional[List[str]] = None,
        append_acquired_knowledge: bool = False
    ) -> None:
        if not self.working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._started_modifying()
        self.working_state.modify_character_knowledge(
            character_id=character_id,
            new_background_knowledge=new_background_knowledge,
            append_background_knowledge=append_background_knowledge,
            new_acquired_knowledge=new_acquired_knowledge,
            append_acquired_knowledge=append_acquired_knowledge
        )

        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def modify_character_dynamic_state(
        self,
        character_id: str,
        new_current_emotion: Optional[str] = None,
        new_immediate_goal: Optional[str] = None
    ) -> None:
        
        character = self.working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot modify the player's dynamic state. Character must be an npc")
        self._started_modifying()
        self.working_state.modify_character_npc_dynamic_state(
            character_id=character_id,
            new_current_emotion=new_current_emotion,
            new_immediate_goal=new_immediate_goal
        )

        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def modify_character_narrative(
        self,
        character_id: str,
        new_narrative_role: Optional[NarrativeRole] = None,
        new_current_narrative_importance: Optional[NarrativeImportance] = None,
        new_narrative_purposes: Optional[List[NarrativePurposeModel]] = None,
        append_narrative_purposes: bool = False
    ) -> None:
        character = self.working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot modify the player's narrative attributes. Character must be an npc")

        self._started_modifying()
        self.working_state.modify_character_npc_narrative(
            character_id=character_id,
            new_narrative_role=new_narrative_role,
            new_current_narrative_importance=new_current_narrative_importance,
            new_narrative_purposes=new_narrative_purposes,
            append_narrative_purposes=append_narrative_purposes
        )

        if character_id not in self._added_characters:
            self._modified_characters.add(character_id)

    def delete_character(self, character_id: str) -> BaseCharacter:
        character = self.working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot delete the player character.")
        
        self._started_modifying()
        
        character=self.working_state.delete_character(character_id):
        if character:
            if character_id not in self._added_characters:
                self._deleted_characters[character_id] = character
            return character
        else:
            raise KeyError(f"Character ID '{character_id}' not found.")

    def place_character(self, character_id: str, scenario_id: str) -> Tuple[BaseCharacter,Scenario]:
        
        character = self.working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        if character.present_in_scenario == scenario_id:
            raise ValueError(f"Character is already present in scenario with ID {scenario_id}")
        
        success, message = self._simulated_game_state.simulated_map.can_place_character(character,scenario_id)
        if not success:
            raise ValueError(message)

        self._started_modifying()

        character = self.working_state.place_character(character_id,scenario_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        return character, self._simulated_game_state.simulated_map.place_character(character,scenario_id)

    def remove_character_from_scenario(self, *args, **kwargs) -> bool:
        self._started_modifying()
        return self.working_state.remove_character_from_scenario(*args, **kwargs)

    def get_character(self, cid: str) -> Optional[BaseCharacter]:
        return self.working_state.find_character(cid)

    def characters_count(self) -> int:
        return self.working_state.characters_count()
