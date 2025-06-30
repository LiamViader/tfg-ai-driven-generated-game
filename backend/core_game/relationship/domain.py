from core_game.relationship.schemas import *
from typing import Dict, Optional

class RelationshipType:
    def __init__(self, data: RelationshipTypeModel):
        self._data: RelationshipTypeModel = data

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def explanation(self) -> Optional[str]:
        return self._data.explanation

    def get_model(self) -> RelationshipTypeModel:
        return self._data

class CharacterRelationship:
    def __init__(self, data: CharacterRelationshipModel):
        self._data: CharacterRelationshipModel = data

    @property
    def type(self) -> RelationshipTypeModel:
        return self._data.type

    @property
    def intensity(self) -> int:
        return self._data.intensity

    def get_model(self) -> CharacterRelationshipModel:
        return self._data

class Relationships:
    """Domain wrapper around character relationships."""

    def __init__(self, relationships_model: Optional[RelationshipsModel] = None) -> None:
        self._relationship_types: Dict[str, RelationshipType]
        self._matrix: Dict[str, Dict[str, Dict[str, CharacterRelationship]]]

        if relationships_model:
            self._populate_from_model(relationships_model)
        else:
            self._relationship_types = {}
            self._matrix = {}

    def _populate_from_model(self, model: RelationshipsModel) -> None:
        self._relationship_types = {
            name: RelationshipType(rt_model)
            for name, rt_model in model.relationship_types.items()
        }
        self._matrix = {}
        for char1_id, nested in model.matrix.items():
            self._matrix[char1_id] = {}
            for char2_id, rel_dict in nested.items():
                self._matrix[char1_id][char2_id] = {
                    rel_name: CharacterRelationship(rel_model)
                    for rel_name, rel_model in rel_dict.items()
                }

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------

    def to_model(self) -> RelationshipsModel:
        """Return the underlying relationships data as a ``RelationshipsModel``."""
        return RelationshipsModel(
            relationship_types={
                name: rt.get_model() for name, rt in self._relationship_types.items()
            },
            matrix={
                src: {
                    tgt: {rname: rel.get_model() for rname, rel in rels.items()}
                    for tgt, rels in nested.items()
                }
                for src, nested in self._matrix.items()
            },
        )

    # ------------------------------------------------------------------
    # Modification methods
    # ------------------------------------------------------------------

    def create_relationship_type(self, name: str, explanation: Optional[str] = None) -> RelationshipType:
        if name in self._relationship_types:
            raise ValueError(f"Relationship type '{name}' already exists.")
        model = RelationshipTypeModel(name=name, explanation=explanation)
        rel_type = RelationshipType(model)
        self._relationship_types[name] = rel_type
        return rel_type

    def create_directed_relationship(
        self,
        source_character_id: str,
        target_character_id: str,
        relationship_type: str,
        intensity: int,
    ) -> CharacterRelationship:
        if relationship_type not in self._relationship_types:
            raise ValueError(f"Unknown relationship type '{relationship_type}'.")
        rel_model = CharacterRelationshipModel(
            type=self._relationship_types[relationship_type].get_model(),
            intensity=intensity,
        )
        rel = CharacterRelationship(rel_model)
        self._matrix.setdefault(source_character_id, {}).setdefault(target_character_id, {})[
            relationship_type
        ] = rel
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
            rel = self._matrix[source_character_id][target_character_id][relationship_type]
        except KeyError as exc:
            raise KeyError("Relationship not found") from exc
        rel._data.intensity = new_intensity

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    def get_relationship_details(
        self,
        source_character_id: str,
        target_character_id: str,
    ) -> Dict[str, CharacterRelationship]:
        return self._matrix.get(source_character_id, {}).get(target_character_id, {})

    def relationship_count(self) -> int:
        count = 0
        for nested in self._matrix.values():
            for rels in nested.values():
                count += len(rels)
        return count

    def get_initial_summary(self) -> str:
        """Return a brief summary of existing relationship data."""
        rel_types = ", ".join(self._relationship_types.keys())
        if not rel_types:
            rel_types = "None"

        character_counts: Dict[str, int] = {}
        for src, nested in self._matrix.items():
            for tgt, rels in nested.items():
                count = len(rels)
                character_counts[src] = character_counts.get(src, 0) + count
                character_counts[tgt] = character_counts.get(tgt, 0) + count

        if not character_counts:
            relationships_summary = "No relationships created yet"
        else:
            relationships_summary = ", ".join(
                f"{cid}: {cnt}" for cid, cnt in character_counts.items()
            )

        return (
            f"Relationship types: {rel_types}. \n" + f"Relationships per character: {relationships_summary}"
        )
