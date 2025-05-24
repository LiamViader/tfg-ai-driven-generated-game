from typing import Dict, List, Optional, Literal, Any, Tuple
from pydantic import BaseModel, Field


class ExitInfo(BaseModel):
    target_scenario_id: str
    connection_type: str = Field(..., description="e.g., 'path', 'door', 'secret_passage'")
    travel_description: Optional[str] = Field(None, description="Small description of the connection if relevant: e.g., 'A dark path descending through gnarled trees.'")
    traversal_conditions: List[str] = Field(default_factory=list, description="e.g., ['requires_rusty_key', 'only_at_night']")
    is_blocked: bool = Field(False, description="Indicates whether this exit is currently blocked and cannot be used.")

Direction = Literal["north", "south", "east", "west", "up", "down"]
OppositeDirections: Dict[Direction, Direction] = {
    "north": "south", "south": "north",
    "east": "west", "west": "east",
    "up": "down", "down": "up"
}

#MES ENDAVANT AFEGIR MÉS ATRIBUTS SI ES TROBA PERTINENT 

class ScenarioModel(BaseModel):
    id: str = Field(..., description="Unique identifier for the scenario.")
    name: str = Field(..., description="Descriptive name of the scenario.")
    visual_description: str = Field(..., description="Detailed description of the visual scenario, what it looks like, key elements, composition, etc.")
    narrative_context: str = Field(..., description="Describes the scenario's significance, history, mood, lore, or key events that occur or have occurred here. Focuses on its role in the story and world.")
    location_type: Literal["interior", "exterior"] = Field(..., description="Indicates whether the scenario is located indoors (interior) or outdoors (exterior).")
    narrative_elements: List[str] = Field(default_factory=list, description="Characters, items, clues, or narrative events present.")
    exits: Dict[Direction, Optional[ExitInfo]] = Field(
        default_factory=lambda: {direction: None for direction in Direction.__args__},
        description="Connections from this scenario to others, by direction."
    )
    origin_relative_position: Optional[Tuple[int, int]] = Field(None, description="Relative (x, y) position with respect to the origin scenario.")
