from pydantic import BaseModel, Field
from typing import Optional, Dict

class RelationshipTypeModel(BaseModel):
    """
    Defines the nature of a relationship (e.g., 'love', 'fear', 'siblings', 'trust').
    """
    name: str = Field(
        ...,
        description="The keyword that defines the relationship (e.g., 'love', 'fear', 'trust', 'siblings')."
    )
    explanation: Optional[str] = Field(
        default=None,
        description="A more detailed explanation of what this relationship type represents in the game, clarifying its meaning and scope if necessary."
    )

class CharacterRelationshipModel(BaseModel):
    """
    Represents a relationship between two characters, including its type and intensity.

    Intensity is measured on a scale from 0 to 10:
    - 0: Total absence or neutrality of the relationship. It does NOT mean the opposite. For example, 'love' with an intensity of 0 means there is no love, but it does NOT imply hate.
    - 10: Maximum possible intensity. For example, 'love' with an intensity of 10 means being completely in love.
    
    For relationships that do not have a measurable intensity (such as 'siblings' or 'parent'), the intensity can be None.
    """
    type: RelationshipTypeModel = Field(
        ...,
        description="The type of relationship being measured."
    )
    intensity: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Level of the relationship on a scale of 0 (neutral/absence) to 10 (maximum). It is None if the relationship does not have an intensity."
    )

class RelationshipsModel(BaseModel):
    """Represents the component of relationships"""
    relationship_types: Dict[str, RelationshipTypeModel] = Field(default_factory=dict, description="stores all the relationship types keyed by its relationshiptype name")
    matrix: Dict[str, Dict[str, Dict[str, CharacterRelationshipModel]]] = Field(default_factory=dict, description="matrix of stored relationships between characters, idcharacter1-idcharacter2-relationshiptypename")
