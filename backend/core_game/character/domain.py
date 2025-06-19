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
    def __init__(self, model: Optional[CharactersModel]=None) -> None:
        self._registry: Dict[str, BaseCharacter]
        self._player: Optional[PlayerCharacter]

        if model:
            self._populate_from_model(model)
        else:
            self._registry={}
            self._player=None

    
    def _populate_from_model(self, model: CharactersModel) -> None:
        self._registry = {character.id: BaseCharacter(character) for character in model.registry.values()}
        self._player = PlayerCharacter(model.player_character) if model.player_character  else None


