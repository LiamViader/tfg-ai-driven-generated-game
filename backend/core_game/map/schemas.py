from typing import Dict, List, Optional, Literal, Any, Tuple, Set
from pydantic import BaseModel, Field
from core_game.map.constants import Direction, OppositeDirections, IndoorOrOutdoor

# Internal counter to generate sequential scenario ids
_scenario_id_counter = 0
# Internal counter to generate sequential connection ids
_connection_id_counter = 0


def generate_scenario_id() -> str:
    """Return a sequential id of the form 'scenario_001'."""
    global _scenario_id_counter
    _scenario_id_counter += 1
    return f"scenario_{_scenario_id_counter:03d}"

def rollback_scenario_id():
    global _scenario_id_counter
    _scenario_id_counter -= 1

def generate_connection_id() -> str:
    """Return a sequential id of the form 'connection_001'."""
    global _connection_id_counter
    _connection_id_counter += 1
    return f"connection_{_connection_id_counter:03d}"

from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS

"""
VALORAR FER AIXÒ PEL CONNECTION TYPE

ConnectionType = Literal[
    "door", "path", "ladder", "stairs", "tunnel", "bridge", "portal", "open_space"
]

connection_type: ConnectionType = Field(..., description=EXIT_FIELDS["connection_type"])"""


class ConnectionModel(BaseModel):
    """Represents a bidirectional connection between two scenarios."""

    id: str = Field(default_factory=generate_connection_id, description="Unique identifier of this connection.")
    scenario_a_id: str = Field(..., description="ID of the first scenario.")
    scenario_b_id: str = Field(..., description="ID of the second scenario.")
    direction_from_a: 'Direction' = Field(..., description="Direction from scenario A towards scenario B.")
    connection_type: str = Field(..., description=EXIT_FIELDS["connection_type"])
    travel_description: Optional[str] = Field(default=None, description=EXIT_FIELDS["travel_description"])
    traversal_conditions: List[str] = Field(default_factory=list, description=EXIT_FIELDS["traversal_conditions"])
    exit_appearance_description: Optional[str] = Field(default=None, description=EXIT_FIELDS["exit_appearance_description"])
    is_blocked: bool = Field(default=False, description=EXIT_FIELDS["is_blocked"])

class ScenarioImageGenerationTemplate(BaseModel):
    """Template for generating scenario images."""
    scene_summary: str = Field(description="A very brief summary of the main scene (1-3 words). Example: 'A floating castle'.")
    scene_detail: str = Field(description="A detailed visual description of the main scene. Example: 'A majestic castle with glowing towers drifts silently among a sea of clouds.'")
    ground_detail: str = Field(description="A detailed description of the ground or base of the scene. Example: 'cracked, ancient stone with glowing blue lava flowing through the fissures.'")
    ground_summary: str = Field(description="A very brief summary of the ground or base (1-3 words). Example: 'Cracked lava stone'.")
    graphic_style: str = Field(description="Defines the artistic look and feel. Examples: 'Oil painting', 'Pixel art', 'Photorealistic 3D render', 'in the style of Studio Ghibli'.")

#valid from i valid until hauran de ser de la classe temps del joc. de moment float com a placeholder

class ScenarioSnapshot(BaseModel):
    valid_from: Optional[float] = Field(default=None, description="Timestamp of when this scenario version was created. If it was the first scenario version then set to None")
    valid_until: float = Field(..., description="Timestamp indicating when this version of the scenario stopped being active.")
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    indoor_or_outdoor: IndoorOrOutdoor = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = Field(..., description=SCENARIO_FIELDS["type"])
    zone: str = Field(..., description=SCENARIO_FIELDS["zone"])
    connections: Dict[Direction, Optional[str]]
    image_path: Optional[str] = Field(default=None, description="Path of the image for the character representation")
    image_generation_prompt: Optional[ScenarioImageGenerationTemplate] = Field(default=None, description="Prompt used for generating the current image.")


class ScenarioModel(BaseModel):
    id: str = Field(default_factory=generate_scenario_id, description="Unique identifier for the scenario.")
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    indoor_or_outdoor: IndoorOrOutdoor = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = Field(..., description=SCENARIO_FIELDS["type"])
    zone: str = Field(..., description=SCENARIO_FIELDS["zone"])
    was_added_this_run: bool = Field(default=True,description="Flag indicating if the scenario was added this run of the graph")
    was_modified_this_run: bool = Field(default=False,description="Flag indicating if the scenario was modified this run of the graph")
    valid_from: Optional[float] = Field(default=None, description="Timestamp of when this scenario version was created. If it was the first scenario version then set to None")
    image_path: Optional[str] = Field(default=None, description="Path of the image for the character representation")
    image_generation_prompt: Optional[ScenarioImageGenerationTemplate] = Field(default=None, description="Prompt used for generating the current image.")
    connections: Dict[Direction, Optional[str]] = Field(
        default_factory=lambda: {direction: None for direction in Direction.__args__},
        description="Mapping from direction to connection ID, if any."
    )
    present_character_ids: set[str] = Field(default_factory=set,description="Ids of the present characters in the map")
    previous_versions: List[ScenarioSnapshot] = Field(
        default_factory=list,
        description="List of previous versions (snapshots) of this scenario."
    )

class GameMapModel(BaseModel):
    scenarios: Dict[str, ScenarioModel] = Field(default_factory=dict, description="Dictionary where key is scenario id and value scenariomodel")
    connections: Dict[str, ConnectionModel] = Field(default_factory=dict, description="Dictionary where key is connection id and value connectioninfo")