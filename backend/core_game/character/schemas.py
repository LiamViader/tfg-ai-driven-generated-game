from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from core_game.character.field_descriptions import *

# Internal counter used for sequential character ids
_character_id_counter = 0


def _generate_character_id() -> str:
    """Return a sequential id of the form 'char_001'."""
    global _character_id_counter
    _character_id_counter += 1
    return f"char_{_character_id_counter:03d}"

class IdentityModel(BaseModel):
    """Core identity traits of the character."""
    full_name: str = Field(..., description=IDENTITY_MODEL_FIELDS["full_name"])
    alias: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["alias"])
    age: int = Field(..., description=IDENTITY_MODEL_FIELDS["age"])
    gender: Literal["male", "female", "non-binary", "undefined", "other"] = Field(..., description=IDENTITY_MODEL_FIELDS["gender"])
    profession: str = Field(..., description=IDENTITY_MODEL_FIELDS["profession"])
    species: str = Field(..., description=IDENTITY_MODEL_FIELDS["species"])
    alignment: str = Field(..., description=IDENTITY_MODEL_FIELDS["alignment"])


class PhysicalAttributesModel(BaseModel):
    """Physical characteristics and appearance."""
    appearance: str = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["appearance"])
    distinctive_features: List[str] = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["distinctive_features"])
    clothing_style: Optional[str] = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["clothing_style"])
    characteristic_items: List[str] = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["characteristic_items"])


class PsychologicalAttributesModel(BaseModel):
    """The character's personality, mind, and backstory."""
    personality_summary: str = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["personality_summary"])
    personality_tags: List[str] = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["personality_tags"])
    motivations: List[str] = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["motivations"])
    values: List[str] = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["values"])
    fears_and_weaknesses: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["fears_and_weaknesses"])
    communication_style: Optional[str] = Field(default=None, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["communication_style"])
    backstory: str = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["backstory"])
    quirks: List[str] = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["quirks"])


class NarrativePurposeModel(BaseModel):
    """Models a character's specific narrative purpose and its visibility."""
    mission: str = Field(..., description=NARRATIVE_PURPOSE_MODEL_FIELDS["mission"])
    is_hidden: bool = Field(False, description=NARRATIVE_PURPOSE_MODEL_FIELDS["is_hidden"])

class NarrativeWeightModel(BaseModel):
    """Defines a character's weight and function within the narrative."""
    narrative_role: Literal["protagonist", "secondary", "extra", "antagonist", "ally", "informational figure"] = Field(..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_role"])
    current_narrative_importance: Literal["important", "secondary", "minor", "inactive"] = Field(..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_importance"])
    narrative_purposes: List[NarrativePurposeModel] = Field(..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_purpose"])

class KnowledgeModel(BaseModel):
    """Tracks the information known by the character."""
    background_knowledge: List[str] = Field(default_factory=list, description=KNOWLEDGE_MODEL_FIELDS["background_knowledge"])
    acquired_knowledge: List[str] = Field(default_factory=list, description=KNOWLEDGE_MODEL_FIELDS["acquired_knowledge"])

class DynamicStateModel(BaseModel):
    """Tracks the character's immediate, changing state."""
    current_emotion: Optional[str] = Field(default=None, description=DYNAMIC_STATE_MODEL_FIELDS["current_emotion"])
    immediate_goal: Optional[str] = Field(default=None, description=DYNAMIC_STATE_MODEL_FIELDS["immediate_goal"])




class CharacterBaseModel(BaseModel):
    """The base model that all character types inherit from."""
    id: str = Field(..., description="Unique identifier for the character.")
    identity: IdentityModel
    physical: PhysicalAttributesModel
    psychological: PsychologicalAttributesModel
    knowledge: KnowledgeModel
    present_in_scenario: Optional[str] = Field(default=None, description="ID of the scenario where the character is currently located.")


class PlayerCharacterModel(CharacterBaseModel):
    """A character controlled by a human player."""
    type: Literal["player"] = Field(default="player", description="Type of character.")


class NonPlayerCharacterModel(CharacterBaseModel):
    """A character controlled by the system (AI)."""
    type: Literal["npc"] = Field(default="npc", description="Type of character.")
    dynamic_state: DynamicStateModel
    narrative: NarrativeWeightModel

class RelationshipType(BaseModel):
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

class CharacterRelationship(BaseModel):
    """
    Represents a relationship between two characters, including its type and intensity.

    Intensity is measured on a scale from 0 to 10:
    - 0: Total absence or neutrality of the relationship. It does NOT mean the opposite. For example, 'love' with an intensity of 0 means there is no love, but it does NOT imply hate.
    - 10: Maximum possible intensity. For example, 'love' with an intensity of 10 means being completely in love.
    
    For relationships that do not have a measurable intensity (such as 'siblings' or 'parent'), the intensity can be None.
    """
    type: RelationshipType = Field(
        ...,
        description="The type of relationship being measured."
    )
    intensity: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Level of the relationship on a scale of 0 (neutral/absence) to 10 (maximum). It is None if the relationship does not have an intensity."
    )