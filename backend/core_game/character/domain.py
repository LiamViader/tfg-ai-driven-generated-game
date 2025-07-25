from typing import Dict, cast, Optional, Tuple, Literal

from .schemas import *

class BaseCharacter:
    def __init__(self, data: CharacterBaseModel):
        self._data = data

    @property
    def id(self) -> str:
        return self._data.id

    @property
    def type(self) -> CharacterType:
        return self._data.type

    @property
    def identity(self) -> IdentityModel:
        return self._data.identity

    @property
    def physical(self) -> PhysicalAttributesModel:
        return self._data.physical

    @property
    def psychological(self) -> PsychologicalAttributesModel:
        return self._data.psychological

    @property
    def knowledge(self) -> KnowledgeModel:
        return self._data.knowledge

    @property
    def present_in_scenario(self) -> Optional[str]:
        return self._data.present_in_scenario
    
    @present_in_scenario.setter
    def present_in_scenario(self, value: Optional[str]) -> None:
        self._data.present_in_scenario = value
    
    @property
    def image_path(self) -> Optional[str]:
        return self._data.image_path
    
    @image_path.setter
    def image_path(self, value: Optional[str]) -> None:
        self._data.image_path = value

    @property
    def image_generation_prompt(self) -> Optional[str]:
        return self._data.image_generation_prompt
    
    @image_generation_prompt.setter
    def image_generation_prompt(self, value: Optional[str]) -> None:
        self._data.image_generation_prompt = value

    def get_model(self) -> CharacterBaseModel:
        return self._data


class PlayerCharacter(BaseCharacter):
    def __init__(self, data: PlayerCharacterModel):
        self._data: PlayerCharacterModel = data
        super().__init__(data)

    def get_model(self) -> PlayerCharacterModel:
        return self._data


class NPCCharacter(BaseCharacter):
    def __init__(self, data: NonPlayerCharacterModel):
        self._data: NonPlayerCharacterModel = data
        super().__init__(data)

    @property
    def dynamic_state(self) -> DynamicStateModel:
        return self._data.dynamic_state

    @property
    def narrative(self) -> NarrativeWeightModel:
        return self._data.narrative

    def get_model(self) -> NonPlayerCharacterModel:
        return self._data


class Characters:
    """Domain wrapper around characters."""

    def __init__(self, model: Optional[CharactersModel] = None) -> None:
        self._registry: Dict[str, BaseCharacter]
        self._player_id: Optional[str]

        if model:
            self._populate_from_model(model)
        else:
            self._registry = {}
            self._player_id = None

    def _populate_from_model(self, model: CharactersModel) -> None:
        self._registry = {}
        for char_id, char_model in model.registry.items():
            if char_model.type == "player":
                self._registry[char_id] = PlayerCharacter(cast(PlayerCharacterModel, char_model))
            else:
                self._registry[char_id] = NPCCharacter(cast(NonPlayerCharacterModel, char_model))

        self._player_id = model.player_character_id


    def to_model(self) -> CharactersModel:
        """Return the underlying data as a CharactersModel."""
        return CharactersModel(
            registry={cid: char.get_model() for cid, char in self._registry.items()},
            # --- CAMBIO AQUÍ ---
            player_character_id=self._player_id,
        )

    def find_character(self, character_id: str) -> Optional[BaseCharacter]:
        """
        Return a character from the registry if it exists, or None.
        Mucho más simple ahora.
        """
        return self._registry.get(character_id)
    
    def get_player(self) -> Optional[PlayerCharacter]:
        return self.player

    def has_player(self) -> bool:
        return self.player is not None

    def add_npc(self, npc:NPCCharacter) -> NPCCharacter:
        """Create a new NPC and return it."""
        self._registry[npc.id] = npc
        return npc

    def add_player(self, player: PlayerCharacter) -> PlayerCharacter:
        """Adds the player to de character components. it does not check anything"""
        if self.has_player():
            raise ValueError("A player character already exists.")
            
        self._registry[player.id] = player
        self._player_id = player.id # La clave es guardar el ID
        return player

    @property
    def player(self) -> Optional[PlayerCharacter]:
        """
        Returns the full PlayerCharacter object by looking it up in the
        registry using its ID. Returns None if there is no player.
        """
        if self._player_id is None:
            return None
        
        char = self._registry.get(self._player_id)
        return cast(PlayerCharacter, char)

    # ------------------------------------------------------------------
    # Modification helpers
    # ------------------------------------------------------------------

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
    ) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False

        if new_full_name is not None:
            char.identity.full_name = new_full_name
        if new_alias is not None:
            char.identity.alias = new_alias
        if new_age is not None:
            char.identity.age = new_age
        if new_gender is not None:
            char.identity.gender = new_gender
        if new_profession is not None:
            char.identity.profession = new_profession
        if new_species is not None:
            char.identity.species = new_species
        if new_alignment is not None:
            char.identity.alignment = new_alignment
        return True

    def modify_character_physical(
        self,
        character_id: str,
        new_appearance: Optional[str] = None,
        new_visual_prompt: Optional[str] = None,
        new_distinctive_features: Optional[List[str]] = None,
        append_distinctive_features: bool = False,
        new_clothing_style: Optional[str] = None,
        new_characteristic_items: Optional[List[str]] = None,
        append_characteristic_items: bool = False,
    ) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False
        if new_appearance is not None:
            char.physical.appearance = new_appearance
        if new_visual_prompt is not None:
            char.physical.visual_prompt = new_visual_prompt
        if new_distinctive_features is not None:
            if append_distinctive_features:
                char.physical.distinctive_features.extend(new_distinctive_features)
            else:
                char.physical.distinctive_features = new_distinctive_features
        if new_clothing_style is not None:
            char.physical.clothing_style = new_clothing_style
        if new_characteristic_items is not None:
            if append_characteristic_items:
                char.physical.characteristic_items.extend(new_characteristic_items)
            else:
                char.physical.characteristic_items = new_characteristic_items
        return True

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
        append_quirks: bool = False,
    ) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False
        p = char.psychological
        if new_personality_summary is not None:
            p.personality_summary = new_personality_summary
        if new_personality_tags is not None:
            if append_personality_tags:
                p.personality_tags.extend(new_personality_tags)
            else:
                p.personality_tags = new_personality_tags
        if new_motivations is not None:
            if append_motivations:
                p.motivations.extend(new_motivations)
            else:
                p.motivations = new_motivations
        if new_values is not None:
            if append_values:
                p.values.extend(new_values)
            else:
                p.values = new_values
        if new_fears_and_weaknesses is not None:
            if append_fears_and_weaknesses:
                p.fears_and_weaknesses.extend(new_fears_and_weaknesses)
            else:
                p.fears_and_weaknesses = new_fears_and_weaknesses
        if new_communication_style is not None:
            p.communication_style = new_communication_style
        if new_backstory is not None:
            p.backstory = new_backstory
        if new_quirks is not None:
            if append_quirks:
                p.quirks.extend(new_quirks)
            else:
                p.quirks = new_quirks
        return True

    def modify_character_knowledge(
        self,
        character_id: str,
        new_background_knowledge: Optional[List[str]] = None,
        append_background_knowledge: bool = False,
        new_acquired_knowledge: Optional[List[str]] = None,
        append_acquired_knowledge: bool = False,
    ) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False
        k = char.knowledge
        if new_background_knowledge is not None:
            if append_background_knowledge:
                k.background_knowledge.extend(new_background_knowledge)
            else:
                k.background_knowledge = new_background_knowledge
        if new_acquired_knowledge is not None:
            if append_acquired_knowledge:
                k.acquired_knowledge.extend(new_acquired_knowledge)
            else:
                k.acquired_knowledge = new_acquired_knowledge
        return True

    def modify_character_npc_dynamic_state(
        self,
        character_id: str,
        new_current_emotion: Optional[str] = None,
        new_immediate_goal: Optional[str] = None,
    ) -> bool:
        char = self.find_character(character_id)
        if not char or not isinstance(char, NPCCharacter):
            return False
        if new_current_emotion is not None:
            char.dynamic_state.current_emotion = new_current_emotion
        if new_immediate_goal is not None:
            char.dynamic_state.immediate_goal = new_immediate_goal
        return True

    def modify_character_npc_narrative(
        self,
        character_id: str,
        new_narrative_role: Optional[NarrativeRole] = None,
        new_current_narrative_importance: Optional[NarrativeImportance] = None,
        new_narrative_purposes: Optional[List[NarrativePurposeModel]] = None,
        append_narrative_purposes: bool = False,
    ) -> bool:
        char = self.find_character(character_id)
        if not char or not isinstance(char, NPCCharacter):
            return False
        n = char.narrative
        if new_narrative_role is not None:
            n.narrative_role = new_narrative_role
        if new_current_narrative_importance is not None:
            n.current_narrative_importance = new_current_narrative_importance
        if new_narrative_purposes is not None:
            if append_narrative_purposes:
                n.narrative_purposes.extend(new_narrative_purposes)
            else:
                n.narrative_purposes = new_narrative_purposes
        return True

    def characters_count(self) -> int:
        return len(self._registry)
    
    def delete_character(self, character_id: str) -> Optional[BaseCharacter]:
        """Delete an NPC from the registry."""
        if character_id == (self.player.id if self.player else None):
            return None
        return self._registry.pop(character_id, None)

    def place_character(self, character: BaseCharacter, new_scenario_id: str) -> Optional[BaseCharacter]:
        char = self.find_character(character.id)
        if char:
            char.present_in_scenario = new_scenario_id
        return char

    def remove_character_from_scenario(self, character_id: str) -> Tuple[Optional[str], Optional[BaseCharacter]]:
        """Removes character from scenario and returns its scenario id"""
        char = self.find_character(character_id)
        if not char or isinstance(char, PlayerCharacter):
            return None, None
        scenario_id = char.present_in_scenario
        char.present_in_scenario = None
        return scenario_id, char
    
    def filter_characters(
        self, 
        attribute_to_filter: Optional[Literal[ "narrative_role","current_narrative_importance", "species","profession","gender","alias","name_contains"]] = None, 
        value_to_match: Optional[str] = None
    ) -> Dict[str, BaseCharacter]:
        
        result: Dict[str, BaseCharacter] = {}
        match_val = (value_to_match or "").lower()

        for char_id, char in self._registry.items():
            if attribute_to_filter is None or value_to_match is None:
                result[char_id] = char
                continue

            value = ""

            if attribute_to_filter == "narrative_role":
                if isinstance(char, NPCCharacter):
                    value = char.narrative.narrative_role
            elif attribute_to_filter == "current_narrative_importance":
                if isinstance(char, NPCCharacter):
                    value = char.narrative.current_narrative_importance
            elif attribute_to_filter == "species":
                value = char.identity.species
            elif attribute_to_filter == "profession":
                value = char.identity.profession
            elif attribute_to_filter == "gender":
                value = char.identity.gender
            elif attribute_to_filter == "alias":
                value = char.identity.alias or ""
            elif attribute_to_filter == "name_contains":
                value = char.identity.full_name

            if match_val in str(value).lower():
                result[char_id] = char

        return result
    
    def group_by_scenario(self) -> Dict[str,List[BaseCharacter]]:
        groups: Dict[str, List[BaseCharacter]] = {}
        for char in self._registry.values():
            scenario = char.present_in_scenario or "OUT_OF_ANY_SCENARIO"
            groups.setdefault(scenario, []).append(
                char
            )
        return groups
    
    def get_characters_at_scenario(self, scenario_id: str) -> List[BaseCharacter]:
        matches = []
        for char in self._registry.values():
            if char.present_in_scenario == scenario_id:
                matches.append(char)
        return matches
    
    def attach_new_image(self, character_id: str, image_path: str, image_generation_prompt: str) -> bool:
        character = self.find_character(character_id)
        if character:
            character.image_path = image_path
            character.image_generation_prompt = image_generation_prompt
            return True
        return False