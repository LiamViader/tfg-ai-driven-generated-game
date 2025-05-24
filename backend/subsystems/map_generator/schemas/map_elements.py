from typing import Dict, List, Optional, Literal, Any # 'any' should be 'Any'
from pydantic import BaseModel, Field

# --- Internal Model Definitions ---

class ExitInfo(BaseModel):
    target_scenario_id: str
    connection_type: str = Field(..., description="e.g., 'path', 'door', 'secret_passage'")
    travel_description: Optional[str] = Field(None, description="e.g., 'A dark path descending through gnarled trees.'")
    traversal_conditions: List[str] = Field(default_factory=list, description="e.g., ['requires_rusty_key', 'only_at_night']")

Direction = Literal["north", "south", "east", "west", "up", "down"]
OppositeDirections: Dict[Direction, Direction] = {
    "north": "south", "south": "north",
    "east": "west", "west": "east",
    "up": "down", "down": "up"
}

class ScenarioModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the scenario.")
    name: str = Field(..., description="Descriptive name of the scenario.")
    description: str = Field(..., description="Detailed description of the environment, key elements, etc.")
    type: str = Field(..., description="Category of the scenario, e.g., 'village', 'dense_forest', 'tavern_interior', 'mountain_path'.")
    narrative_elements: List[str] = Field(default_factory=list, description="Characters, items, clues, or narrative events present.")
    exits: Dict[Direction, Optional[ExitInfo]] = Field(
        default_factory=lambda: {direction: None for direction in Direction.__args__}, # type: ignore
        description="Connections from this scenario to others, by direction."
    )
    # Optional fields
    debug_relative_position: Optional[str] = Field(None, description="Helps debug conceptual spatial layout.")
    special_attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional scenario-specific properties.")
