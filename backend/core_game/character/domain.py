from typing import Dict, cast, Optional

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
        self._player: Optional[PlayerCharacter]

        if model:
            self._populate_from_model(model)
        else:
            self._registry = {}
            self._player = None

    def _populate_from_model(self, model: CharactersModel) -> None:
        self._registry = {
            character.id: BaseCharacter(character)
            for character in model.registry.values()
        }
        self._player = (
            PlayerCharacter(model.player_character) if model.player_character else None
        )

    # ------------------------------------------------------------------
    # Basic accessors
    # ------------------------------------------------------------------

    def to_model(self) -> CharactersModel:
        """Return the underlying data as a CharactersModel."""
        return CharactersModel(
            registry={cid: char.get_model() for cid, char in self._registry.items()},
            player_character=self._player.get_model() if self._player else None,
        )

    def find_character(self, character_id: str) -> Optional[BaseCharacter]:
        """Return a character if it exists, or None."""
        if self._player and self._player.id == character_id:
            return self._player
        return self._registry.get(character_id)

    # ------------------------------------------------------------------
    # Creation helpers
    # ------------------------------------------------------------------

    def create_npc(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        narrative: NarrativeWeightModel,
        knowledge: Optional[KnowledgeModel] = None,
        dynamic_state: Optional[DynamicStateModel] = None,
    ) -> NPCCharacter:
        """Create a new NPC and return it."""

        knowledge = knowledge or KnowledgeModel()
        dynamic_state = dynamic_state or DynamicStateModel()

        new_id = CharactersModel.generate_sequential_character_id(list(self._registry.keys()))  # type: ignore
        npc_model = NonPlayerCharacterModel(
            id=new_id,
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=None,
            dynamic_state=dynamic_state,
            narrative=narrative,
        )
        npc = NPCCharacter(npc_model)
        self._registry[new_id] = npc
        return npc

    def create_player(
        self,
        identity: IdentityModel,
        physical: PhysicalAttributesModel,
        psychological: PsychologicalAttributesModel,
        present_in_scenario: str,
        knowledge: Optional[KnowledgeModel] = None,
    ) -> PlayerCharacter:
        """Create the player character. Raises ValueError if it already exists."""

        if self._player is not None:
            raise ValueError("Player already exists")

        knowledge = knowledge or KnowledgeModel()
        new_id = CharactersModel.generate_sequential_character_id(list(self._registry.keys()))  # type: ignore
        player_model = PlayerCharacterModel(
            id=new_id,
            identity=identity,
            physical=physical,
            psychological=psychological,
            knowledge=knowledge,
            present_in_scenario=present_in_scenario,
        )

        player = PlayerCharacter(player_model)
        self._player = player
        self._registry[new_id] = player
        return player

    # ------------------------------------------------------------------
    # Modification helpers
    # ------------------------------------------------------------------

    def delete_character(self, character_id: str) -> bool:
        """Delete an NPC from the registry."""
        if character_id == (self._player.id if self._player else None):
            return False
        return self._registry.pop(character_id, None) is not None

    def place_character(self, character_id: str, new_scenario_id: str) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False
        char.get_model().present_in_scenario = new_scenario_id
        return True

    def remove_character_from_scenario(self, character_id: str) -> bool:
        char = self.find_character(character_id)
        if not char or isinstance(char, PlayerCharacter):
            return False
        char.get_model().present_in_scenario = None
        return True

    def modify_identity(
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

    def modify_physical(
        self,
        character_id: str,
        new_appearance: Optional[str] = None,
        new_distinctive_features: Optional[list] = None,
        append_distinctive_features: bool = False,
        new_clothing_style: Optional[str] = None,
        new_characteristic_items: Optional[list] = None,
        append_characteristic_items: bool = False,
    ) -> bool:
        char = self.find_character(character_id)
        if not char:
            return False
        if new_appearance is not None:
            char.physical.appearance = new_appearance
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

    def modify_psychological(
        self,
        character_id: str,
        new_personality_summary: Optional[str] = None,
        new_personality_tags: Optional[list] = None,
        append_personality_tags: bool = False,
        new_motivations: Optional[list] = None,
        append_motivations: bool = False,
        new_values: Optional[list] = None,
        append_values: bool = False,
        new_fears_and_weaknesses: Optional[list] = None,
        append_fears_and_weaknesses: bool = False,
        new_communication_style: Optional[str] = None,
        new_backstory: Optional[str] = None,
        new_quirks: Optional[list] = None,
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

    def modify_knowledge(
        self,
        character_id: str,
        new_background_knowledge: Optional[list] = None,
        append_background_knowledge: bool = False,
        new_acquired_knowledge: Optional[list] = None,
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

    def modify_dynamic_state(
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

    def modify_narrative(
        self,
        character_id: str,
        new_narrative_role: Optional[NarrativeRole] = None,
        new_current_narrative_importance: Optional[NarrativeImportance] = None,
        new_narrative_purposes: Optional[list] = None,
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
