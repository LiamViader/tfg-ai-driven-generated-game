from typing import Dict

from .schemas import (
    CharacterBaseModel,
    PlayerCharacterModel,
    RelationshipType,
    CharacterRelationship,
)


class Characters:
    """Domain wrapper around the collection of all game characters."""

    def __init__(
        self,
        registry: Dict[str, CharacterBaseModel],
        player_character: PlayerCharacterModel,
    ) -> None:
        self.registry = registry
        self.player = player_character

    def add(self, character: CharacterBaseModel) -> None:
        self.registry[character.id] = character

    def get(self, character_id: str) -> CharacterBaseModel | None:
        return self.registry.get(character_id)


class Relationships:
    """Domain wrapper around character relationships."""

    def __init__(
        self,
        relationship_types: Dict[str, RelationshipType],
        matrix: Dict[str, Dict[str, Dict[str, CharacterRelationship]]],
    ) -> None:
        self.relationship_types = relationship_types
        self.matrix = matrix

    def get(
        self, source: str, target: str, relationship_type: str
    ) -> CharacterRelationship | None:
        return (
            self.matrix.get(source, {})
            .get(target, {})
            .get(relationship_type)
        )
