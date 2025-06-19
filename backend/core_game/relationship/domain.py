from core_game.relationship.schemas import *
from typing import Dict

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
    def intensity(self) -> Optional[int]:
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
