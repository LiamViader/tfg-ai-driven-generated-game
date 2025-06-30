from copy import deepcopy
from typing import Dict, Optional

from core_game.relationship.domain import Relationships, RelationshipType, CharacterRelationship
from core_game.relationship.schemas import (
    RelationshipsModel,
    RelationshipTypeModel,
    CharacterRelationshipModel,
)


class SimulatedRelationships:
    """Lightweight wrapper around :class:`Relationships` for isolated modifications."""

    def __init__(self, relationships: Relationships) -> None:
        self._working_state: Relationships = relationships

    def __deepcopy__(self, memo):
        copied_relationships = Relationships(relationships_model=deepcopy(self._working_state.to_model()))
        return SimulatedRelationships(copied_relationships)

    def get_state(self) -> Relationships:
        return self._working_state

    # ---- Modification methods ----
    def create_relationship_type(self, name: str, explanation: Optional[str] = None) -> RelationshipType:
        return self._working_state.create_relationship_type(name=name, explanation=explanation)

    def create_directed_relationship(
        self,
        source_character_id: str,
        target_character_id: str,
        relationship_type: str,
        intensity: int,
    ) -> CharacterRelationship:
        return self._working_state.create_directed_relationship(
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            relationship_type=relationship_type,
            intensity=intensity,
        )

    def create_undirected_relationship(
        self,
        character_a_id: str,
        character_b_id: str,
        relationship_type: str,
        intensity: int,
    ) -> None:
        self._working_state.create_undirected_relationship(
            character_a_id=character_a_id,
            character_b_id=character_b_id,
            relationship_type=relationship_type,
            intensity=intensity,
        )

    def modify_relationship_intensity(
        self,
        source_character_id: str,
        target_character_id: str,
        relationship_type: str,
        new_intensity: int,
    ) -> None:
        self._working_state.modify_relationship_intensity(
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            relationship_type=relationship_type,
            new_intensity=new_intensity,
        )

    # ---- Read methods ----
    def get_relationship_details(
        self, source_character_id: str, target_character_id: str
    ) -> Dict[str, CharacterRelationship]:
        return self._working_state.get_relationship_details(source_character_id, target_character_id)

    def relationship_count(self) -> int:
        return self._working_state.relationship_count()

    def get_initial_summary(self) -> str:
        """Return a brief summary of existing relationship data."""
        return self._working_state.get_initial_summary()
