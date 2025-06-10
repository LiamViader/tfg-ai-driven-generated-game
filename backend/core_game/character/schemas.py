from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from core_game.character.field_descriptions import *

class IdentityModel(BaseModel):
    """Core identity traits of the character."""
    full_name: str = Field(..., description=IDENTITY_MODEL_FIELDS["full_name"])
    alias: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["alias"])
    age: Optional[int] = Field(default=None, description=IDENTITY_MODEL_FIELDS["age"])
    gender: Literal["male", "female", "non-binary", "undefined", "other"] = Field(..., description=IDENTITY_MODEL_FIELDS["gender"])
    profession: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["profession"])
    species: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["species"])
    alignment: Optional[str] = Field(default=None, description=IDENTITY_MODEL_FIELDS["alignment"])


class PhysicalAttributesModel(BaseModel):
    """Physical characteristics and appearance."""
    appearance: str = Field(..., description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["appearance"])
    distinctive_features: List[str] = Field(default_factory=list, description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["distinctive_features"])
    clothing_style: Optional[str] = Field(default=None, description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["clothing_style"])
    characteristic_items: List[str] = Field(default_factory=list, description=PHYSICAL_ATTRIBUTES_MODEL_FIELDS["characteristic_items"])


class PsychologicalAttributesModel(BaseModel):
    """The character's personality, mind, and backstory."""
    personality_summary: str = Field(..., description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["personality_summary"])
    personality_tags: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["personality_tags"])
    motivations: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["motivations"])
    values: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["values"])
    fears_and_weaknesses: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["fears_and_weaknesses"])
    communication_style: Optional[str] = Field(default=None, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["communication_style"])
    backstory: Optional[str] = Field(default=None, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["backstory"])
    quirks: List[str] = Field(default_factory=list, description=PSYCHOLOGICAL_ATTRIBUTES_MODEL_FIELDS["quirks"])


class NarrativePurposeModel(BaseModel):
    """Models a character's specific narrative purpose and its visibility."""
    mission: str = Field(..., description=NARRATIVE_PURPOSE_MODEL_FIELDS["mission"])
    is_hidden: bool = Field(False, description=NARRATIVE_PURPOSE_MODEL_FIELDS["is_hidden"])

class NarrativeWeightModel(BaseModel):
    """Defines a character's weight and function within the narrative."""
    narrative_role: str = Field(..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_role"])
    narrative_importance: Literal["important", "secondary", "minor", "inactive"] = Field(..., description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_importance"])
    narrative_purpose: List[NarrativePurposeModel] = Field(default_factory=list, description=NARRATIVE_WEIGHT_MODEL_FIELDS["narrative_purpose"])

class KnowledgeModel(BaseModel):
    """Tracks the information known by the character."""
    background_knowledge: List[str] = Field(default_factory=list, description=KNOWLEDGE_MODEL_FIELDS["background_knowledge"])
    acquired_knowledge: List[str] = Field(default_factory=list, description=KNOWLEDGE_MODEL_FIELDS["acquired_knowledge"])


class DynamicStateModel(BaseModel):
    """Tracks the character's immediate, changing state."""
    current_emotion: Optional[str] = Field(default=None, description=DYNAMIC_STATE_MODEL_FIELDS["current_emotion"])
    immediate_goal: Optional[str] = Field(default=None, description=DYNAMIC_STATE_MODEL_FIELDS["immediate_goal"])




class CharacterBase(BaseModel):
    """The base model that all character types inherit from."""
    id: str = Field(..., description="Unique identifier for the character.")
    identity: IdentityModel
    physical: PhysicalAttributesModel
    psychological: PsychologicalAttributesModel
    knowledge: KnowledgeModel
    present_in_scenario: Optional[str] = Field(default=None, description="ID of the scenario where the character is currently located.")


class PlayerCharacter(CharacterBase):
    """A character controlled by a human player."""
    type: Literal["player"] = Field(default="player", description="Type of character.")


class NonPlayerCharacter(CharacterBase):
    """A character controlled by the system (AI)."""
    type: Literal["npc"] = Field(default="npc", description="Type of character.")
    dynamic_state: DynamicStateModel
    narrative: NarrativeWeightModel