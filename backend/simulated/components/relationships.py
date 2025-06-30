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
        rel_types = {
            name: deepcopy(rel_type.get_model())
            for name, rel_type in self._working_state._relationship_types.items()
        }
        matrix: Dict[str, Dict[str, Dict[str, CharacterRelationshipModel]]] = {}
        for src, nested in self._working_state._matrix.items():
            matrix[src] = {}
            for tgt, rels in nested.items():
                matrix[src][tgt] = {
                    name: deepcopy(rel.get_model()) for name, rel in rels.items()
                }
        new_model = RelationshipsModel(relationship_types=rel_types, matrix=matrix)
        return SimulatedRelationships(Relationships(new_model))

    def get_state(self) -> Relationships:
        return self._working_state

    # ---- Modification methods ----
    def create_relationship_type(self, name: str, explanation: Optional[str] = None) -> RelationshipType:
        if name in self._working_state._relationship_types:
            raise ValueError(f"Relationship type '{name}' already exists.")
        model = RelationshipTypeModel(name=name, explanation=explanation)
        rel_type = RelationshipType(model)
        self._working_state._relationship_types[name] = rel_type
        return rel_type

    def create_directed_relationship(
        self,
        source_character_id: str,
        target_character_id: str,
        relationship_type: str,
        intensity: int,
    ) -> CharacterRelationship:
        if relationship_type not in self._working_state._relationship_types:
            raise ValueError(f"Unknown relationship type '{relationship_type}'.")
        rel_model = CharacterRelationshipModel(
            type=self._working_state._relationship_types[relationship_type].get_model(),
            intensity=intensity,
        )
        rel = CharacterRelationship(rel_model)
        self._working_state._matrix.setdefault(source_character_id, {}).setdefault(target_character_id, {})[relationship_type] = rel
        return rel

    def create_undirected_relationship(
        self,
        character_a_id: str,
        character_b_id: str,
        relationship_type: str,
        intensity: int,
    ) -> None:
        self.create_directed_relationship(character_a_id, character_b_id, relationship_type, intensity)
        self.create_directed_relationship(character_b_id, character_a_id, relationship_type, intensity)

    def modify_relationship_intensity(
        self,
        source_character_id: str,
        target_character_id: str,
        relationship_type: str,
        new_intensity: int,
    ) -> None:
        try:
            rel = self._working_state._matrix[source_character_id][target_character_id][relationship_type]
        except KeyError as exc:
            raise KeyError("Relationship not found") from exc
        rel._data.intensity = new_intensity

    # ---- Read methods ----
    def get_relationship_details(
        self, source_character_id: str, target_character_id: str
    ) -> Dict[str, CharacterRelationship]:
        return self._working_state._matrix.get(source_character_id, {}).get(target_character_id, {})

    def relationship_count(self) -> int:
        count = 0
        for nested in self._working_state._matrix.values():
            for rels in nested.values():
                count += len(rels)
        return count
