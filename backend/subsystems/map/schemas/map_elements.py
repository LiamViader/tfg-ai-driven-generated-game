from typing import Dict, List, Optional, Literal, Any, Tuple
from pydantic import BaseModel, Field
from .descriptions import SCENARIO_FIELDS, EXIT_FIELDS


class ExitInfo(BaseModel):
    target_scenario_id: str
    connection_type: str = Field(..., description=EXIT_FIELDS["connection_type"])
    travel_description: Optional[str] = Field(None, description=EXIT_FIELDS["travel_description"])
    traversal_conditions: List[str] = Field(default_factory=list, description=EXIT_FIELDS["traversal_conditions"])
    is_blocked: bool = Field(False, description=EXIT_FIELDS["is_blocked"])

Direction = Literal["north", "south", "east", "west"]
OppositeDirections: Dict[Direction, Direction] = {
    "north": "south", "south": "north",
    "east": "west", "west": "east"
}

#MES ENDAVANT AFEGIR MÉS ATRIBUTS SI ES TROBA PERTINENT 

class ScenarioModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the scenario.")
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    indoor_or_outdoor: Literal["indoor", "outdoor"] = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    narrative_elements: List[str] = Field(default_factory=list, description="Characters, items, clues, or narrative events present.")
    exits: Dict[Direction, Optional[ExitInfo]] = Field(
        default_factory=lambda: {direction: None for direction in Direction.__args__},
        description="Connections from this scenario to others, by direction."
    )
    origin_relative_position: Optional[Tuple[int, int]] = Field(None, description="Relative (x, y) position with respect to the origin scenario.")
