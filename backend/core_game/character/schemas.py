from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from core_game.relationship.schemas import RelationshipTypeModel as RelationshipType
from core_game.character.constants import (
    Gender,
    CharacterType,
    NarrativeRole,
    NarrativeImportance,
)
from core_game.character.field_descriptions import *

# Internal counter used for sequential character ids
_character_id_counter = 0


def generate_character_id() -> str:
    """Return a sequential id of the form 'character_001'."""
    global _character_id_counter
    _character_id_counter += 1
    return f"character_{_character_id_counter:03d}"

def rollback_character_id():
    global _character_id_counter
    _character_id_counter -= 1

class IdentityModel(BaseModel):
    """Core identity traits of the character."""
    full_name: str = Field(..., description=IDENTITY_MODEL_FIELDS["full_name"])
    alias: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["alias"])
    age: int = Field(..., description=IDENTITY_MODEL_FIELDS["age"])
    gender: Gender = Field(..., description=IDENTITY_MODEL_FIELDS["gender"])
    profession: str = Field(..., description=IDENTITY_MODEL_FIELDS["profession"])
    species: str = Field(..., description=IDENTITY_MODEL_FIELDS["species"])
    alignment: str = Field(..., description=IDENTITY_MODEL_FIELDS["alignment"])


class PhysicalAttributesModel(BaseModel):
    """Physical characteristics and appearance."""
    appearance: str = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["appearance"])
    visual_prompt: str = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["visual_prompt"])
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
    narrative_role: NarrativeRole = Field(
        ..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_role"]
    )
    current_narrative_importance: NarrativeImportance = Field(
        ..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_importance"]
    )
    narrative_purposes: List[NarrativePurposeModel] = Field(
        ..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_purpose"]
    )

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
    id: str = Field(default_factory=generate_character_id, description="Unique identifier for the character.")
    type: CharacterType = Field(default="player", description="Type of character.")
    identity: IdentityModel
    physical: PhysicalAttributesModel
    psychological: PsychologicalAttributesModel
    knowledge: KnowledgeModel
    present_in_scenario: Optional[str] = Field(default=None, description="ID of the scenario where the character is currently located.")


class PlayerCharacterModel(CharacterBaseModel):
    """A character controlled by a human player."""
    type: CharacterType = Field(default="player", description="Type of character.")


class NonPlayerCharacterModel(CharacterBaseModel):
    """A character controlled by the system (AI)."""
    type: CharacterType = Field(default="npc", description="Type of character.")
    dynamic_state: DynamicStateModel
    narrative: NarrativeWeightModel


class CharactersModel(BaseModel):
    """"
    Represents the component of characters
    """
    registry: Dict[str, CharacterBaseModel] = Field(default_factory=dict,description="Dictionary mapping each character id to correspondent CharacterBaseModel")
    player_character: Optional[PlayerCharacterModel] = Field(default=None, description="Player character")
