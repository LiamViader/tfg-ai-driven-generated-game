from typing import Dict, List, Optional, Literal, Any, Tuple, Set
from pydantic import BaseModel, Field
from .descriptions import SCENARIO_FIELDS, EXIT_FIELDS

"""
VALORAR FER AIXÒ PEL CONNECTION TYPE

ConnectionType = Literal[
    "door", "path", "ladder", "stairs", "tunnel", "bridge", "portal", "open_space"
]

connection_type: ConnectionType = Field(..., description=EXIT_FIELDS["connection_type"])"""


class ExitInfo(BaseModel):
    target_scenario_id: str = Field(..., description="Unique identifier of the target scenario the exit points to.")
    connection_type: str = Field(..., description=EXIT_FIELDS["connection_type"])
    travel_description: Optional[str] = Field(default=None, description=EXIT_FIELDS["travel_description"])
    traversal_conditions: List[str] = Field(default_factory=list, description=EXIT_FIELDS["traversal_conditions"])
    exit_appearance_description: Optional[str] = Field(default=None, description=EXIT_FIELDS["exit_appearance_description"])
    is_blocked: bool = Field(default=False, description=EXIT_FIELDS["is_blocked"])

Direction = Literal["north", "south", "east", "west"]
OppositeDirections: Dict[Direction, Direction] = {
    "north": "south", "south": "north",
    "east": "west", "west": "east"
}

#valid from i valid until hauran de ser de la classe temps del joc. de moment float com a placeholder

class ScenarioSnapshot(BaseModel):
    valid_from: Optional[float] = Field(default=None, description="Timestamp of when this scenario version was created. If it was the first scenario version then set to None")
    valid_until: float = Field(..., description="Timestamp indicating when this version of the scenario stopped being active.")
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    indoor_or_outdoor: Literal["indoor", "outdoor"] = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = Field(..., description=SCENARIO_FIELDS["type"])
    zone: str = Field(..., description=SCENARIO_FIELDS["zone"])
    exits: Dict[Direction, Optional[ExitInfo]]


class ScenarioModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the scenario.")
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    indoor_or_outdoor: Literal["indoor", "outdoor"] = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = Field(..., description=SCENARIO_FIELDS["type"])
    zone: str = Field(..., description=SCENARIO_FIELDS["zone"])
    was_added_this_run: bool = Field(default=True,description="Flag indicating if the scenario was added this run of the graph")
    was_modified_this_run: bool = Field(default=False,description="Flag indicating if the scenario was modified this run of the graph")
    valid_from: Optional[float] = Field(default=None, description="Timestamp of when this scenario version was created. If it was the first scenario version then set to None")
    exits: Dict[Direction, Optional[ExitInfo]] = Field(
        default_factory=lambda: {direction: None for direction in Direction.__args__},
        description="Connections from this scenario to others, by direction."
    )
    previous_versions: List[ScenarioSnapshot] = Field(
        default_factory=list,
        description="List of previous versions (snapshots) of this scenario."
    )

    def snapshot_scenario(self, current_time: float):
        snapshot = ScenarioSnapshot(
            name=self.name,
            visual_description=self.visual_description,
            narrative_context=self.narrative_context,
            summary_description=self.summary_description,
            indoor_or_outdoor=self.indoor_or_outdoor,
            type=self.type,
            zone=self.zone,
            exits=self.exits.copy(),  # Copiem la dict
            valid_from=self.valid_from,
            valid_until=current_time
        )
        self.previous_versions.append(snapshot)

