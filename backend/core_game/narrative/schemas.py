from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class GoalModel(BaseModel):
    """Defines a main goal for the player in the narrative. This will guide the narrative."""
    description: str = Field(..., description="Clear description of the goal to be achieved.")

class NarrativeBeatModel(BaseModel):
    """Represents a unit of narrative progress."""
    id: str = Field(..., description="Unique identifier of the narrative beat.")
    description: str = Field(..., description="Description of the goal/s or event/s represented by the beat.")
    status: Literal["PENDING", "ACTIVE", "COMPLETED", "FAILED", "DISCARDED"] = Field("PENDING", description="Current status of the beat.")
    origin: Optional[Literal["NARRATIVE_STAGE", "FAILURE_CONDITION"]] = Field(None, description="Where this beat originates from (narrative stage or failure condition).")
    priority: Optional[int] = Field(10, description="Priority of this beat compared to others (lower is higher priority).")

class RiskTriggeredBeats(BaseModel):
    trigger_risk_level: int = Field(..., ge=0, le=100, description="Risk level at which the beats become active.")
    deactivate_risk_level: int = Field(..., ge=0, le=100, description="Risk level below which the beats become inactive again.")
    beats: List[NarrativeBeatModel] = Field(default_factory=list, description="Narrative beat to trigger.")

class FailureConditionModel(BaseModel):
    """Defines a condition that can lead to an undesired narrative ending."""
    id: str = Field(...,description="Failure condition id")
    description: str = Field(..., description="Description of the failure condition.")
    risk_level: int = Field(0, ge=0, le=100, description="Current risk level (0-100).")
    is_active: bool = Field(False, description="Indicates whether this failure condition has been fully triggered (risk level reached 100) and the narrative has failed as a result.")
    risk_triggered_beats: List[RiskTriggeredBeats] = Field(default_factory=list, description="List of risk level ranges mapped to narrative beats that should be triggered when the risk is within those ranges.")

class NarrativeStageTypeModel(BaseModel):
    """Defines a stage in a narrative structure type (static info only)."""
    name: str = Field(..., description="Stage name e.g. Introduction, climax, etc.")
    narrative_objectives: str = Field(
        ..., description="General objectives for this stage, e.g., introducing characters, presenting conflicts, revealing the world, etc."
    )


class NarrativeStageModel(NarrativeStageTypeModel):
    """Represents a stage in an active narrative structure with beats."""
    stage_beats: List[NarrativeBeatModel] = Field(
        default_factory=list, description="Available narrative beats in the stage"
    )

class NarrativeStructureTypeModel(BaseModel):
    """Static definition of a narrative structure without concrete beats."""
    name: str = Field(..., description="Name of the narrative structure e.g. 5 act, Hero's journey")
    description: str = Field(..., description="General description of the narrative structure and its logic.")
    orientative_use_cases: str = Field(
        ..., description="Typical use cases for this structure (genres or tones where it works well)."
    )
    stages: List[NarrativeStageTypeModel] = Field(
        default_factory=list, description="Ordered stages that define this structure"
    )


class NarrativeStructureModel(BaseModel):
    """Active narrative structure that contains dynamic beats."""
    structure_type: NarrativeStructureTypeModel = Field(
        ..., description="Reference to the static narrative structure definition."
    )
    stages: List[NarrativeStageModel] = Field(
        default_factory=list, description="Stages of this structure with their narrative beats"
    )

class NarrativeStateModel(BaseModel):
    """Tracks the state of the plot, goals, and progression."""
    main_goal: Optional[GoalModel] = Field(None, description="The main goal of the narrative.")
    failure_conditions: List[FailureConditionModel] = Field(default_factory=list, description="List of failure conditions.")
    current_stage_index: Optional[int] = Field(0, description="Index of the currently active narrative stage.")
    narrative_structure: NarrativeStructureModel = Field(
        ..., description="Narrative structure selected for the narrative."
    )
