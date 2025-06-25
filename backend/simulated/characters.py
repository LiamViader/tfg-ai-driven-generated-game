from copy import deepcopy
from typing import Optional, Dict, Set, Tuple, List, TYPE_CHECKING, Literal

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
from simulated.decorators import requires_modification

class SimulatedCharacters:
    """Lightweight wrapper around :class:`Characters` for isolated modifications."""

    def __init__(self, characters: Characters, simulated_game_state: 'SimulatedGameState', is_modifiable: bool = False) -> None:
        self._working_state: Characters = characters
        self._simulated_game_state: 'SimulatedGameState' = simulated_game_state
        self._is_modifiable: bool = is_modifiable

    def __deepcopy__(self, memo):
        copied_characters = Characters(model=deepcopy(self._working_state.to_model()))
        new_copy = SimulatedCharacters(
            characters=copied_characters,
            simulated_game_state=self._simulated_game_state,
            is_modifiable=True 
        )
        return new_copy


    @requires_modification
    def create_npc(
        self, 
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        narrative: NarrativeWeightModel,
        knowledge: KnowledgeModel,
        dynamic_state: DynamicStateModel = DynamicStateModel()
    ) -> NPCCharacter:
        

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

        return npc

    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        scenario_id: str,
        knowledge: Optional[KnowledgeModel] = KnowledgeModel()
    ) -> Tuple[PlayerCharacter, Scenario]:

        if self._working_state.has_player():
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
        
        scenario = self._simulated_game_state.simulated_map.place_player(player,scenario_id)
        player = self._working_state.add_player(player)

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
        if not self._working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._working_state.modify_character_identity(
            character_id=character_id,
            new_full_name=new_full_name,
            new_alias=new_alias,
            new_age=new_age,
            new_gender=new_gender,
            new_profession=new_profession,
            new_species=new_species,
            new_alignment=new_alignment
        )

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
        
        if not self._working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._working_state.modify_character_physical(
            character_id=character_id,
            new_appearance=new_appearance,
            new_distinctive_features=new_distinctive_features,
            append_distinctive_features=append_distinctive_features,
            new_clothing_style=new_clothing_style,
            new_characteristic_items=new_characteristic_items,
            append_characteristic_items=append_characteristic_items,
        )

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
        if not self._working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        self._working_state.modify_character_psychological(
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


    def modify_character_knowledge(
        self,
        character_id: str,
        new_background_knowledge: Optional[List[str]] = None,
        append_background_knowledge: bool = False,
        new_acquired_knowledge: Optional[List[str]] = None,
        append_acquired_knowledge: bool = False
    ) -> None:
        if not self._working_state.find_character(character_id):
            raise KeyError(f"Character with ID '{character_id}' not found.")

        self._working_state.modify_character_knowledge(
            character_id=character_id,
            new_background_knowledge=new_background_knowledge,
            append_background_knowledge=append_background_knowledge,
            new_acquired_knowledge=new_acquired_knowledge,
            append_acquired_knowledge=append_acquired_knowledge
        )

    def modify_character_dynamic_state(
        self,
        character_id: str,
        new_current_emotion: Optional[str] = None,
        new_immediate_goal: Optional[str] = None
    ) -> None:
        
        character = self._working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot modify the player's dynamic state. Character must be an npc")

        self._working_state.modify_character_npc_dynamic_state(
            character_id=character_id,
            new_current_emotion=new_current_emotion,
            new_immediate_goal=new_immediate_goal
        )


    def modify_character_narrative(
        self,
        character_id: str,
        new_narrative_role: Optional[NarrativeRole] = None,
        new_current_narrative_importance: Optional[NarrativeImportance] = None,
        new_narrative_purposes: Optional[List[NarrativePurposeModel]] = None,
        append_narrative_purposes: bool = False
    ) -> None:
        character = self._working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot modify the player's narrative attributes. Character must be an npc")

        self._working_state.modify_character_npc_narrative(
            character_id=character_id,
            new_narrative_role=new_narrative_role,
            new_current_narrative_importance=new_current_narrative_importance,
            new_narrative_purposes=new_narrative_purposes,
            append_narrative_purposes=append_narrative_purposes
        )


    def delete_character(self, character_id: str) -> BaseCharacter:
        character = self._working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot delete the player character.")
        
        character=self._working_state.delete_character(character_id)
        if character:
            return character
        else:
            raise KeyError(f"Character ID '{character_id}' not found.")

    def place_character(self, character_id: str, scenario_id: str) -> Tuple[BaseCharacter,Scenario]:
        
        character = self._working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        if character.present_in_scenario == scenario_id:
            raise ValueError(f"Character is already present in scenario with ID {scenario_id}")
        
        success, message = self._simulated_game_state.simulated_map.can_place_character(character,scenario_id)
        if not success:
            raise ValueError(message)


        character = self._working_state.place_character(character_id,scenario_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        
        return character, self._simulated_game_state.simulated_map.place_character(character,scenario_id)

    def remove_character_from_scenario(self, character_id: str) -> Tuple[BaseCharacter,Scenario]:
        character = self._working_state.find_character(character_id)
        if not character:
            raise KeyError(f"Character with ID '{character_id}' not found.")
        if isinstance(character, PlayerCharacterModel):
            raise ValueError("Cannot remove the player from a scenario.")

        scenario_id, character = self._working_state.remove_character_from_scenario(character_id)
        if not scenario_id or not character:
            raise ValueError("Character is already not present in any scenario.")
        
        scenario = self._simulated_game_state.simulated_map.remove_character_from_scenario(character, scenario_id)
        return character, scenario

    def get_character(self, cid: str) -> Optional[BaseCharacter]:
        return self._working_state.find_character(cid)
    
    def get_player(self) -> Optional[PlayerCharacter]:
        return self._working_state.get_player()

    def characters_count(self) -> int:
        return self._working_state.characters_count()
    
    def filter_characters(
            self, 
            attribute_to_filter: Optional[Literal[ "narrative_role","current_narrative_importance", "species","profession","gender","alias","name_contains"]] = None, 
            value_to_match: Optional[str] = None
        ) -> Dict[str, BaseCharacter]:
        return self._working_state.filter_characters(attribute_to_filter,value_to_match)

    def group_by_scenario(self) -> Dict[str,List[BaseCharacter]]:
        return self._working_state.group_by_scenario()

    def get_initial_summary(self) -> str:
        characters = self.filter_characters(None, None)
        if not characters:
            return "No characters created yet."
        return f"Cast has {self.characters_count()} Characters{", and no player character yet" if not self._working_state.has_player() else ""}: " + ", ".join(f"{c.identity.full_name}({cid})" for cid, c in characters.items())