from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from subsystems.map.schemas.map_elements import ScenarioModel

class MapModel(BaseModel):
    nodes: Dict[str, ScenarioModel] = Field(
        default_factory=dict,
        description="Mapping of scenario IDs to their corresponding ScenarioModel."
    )
    localitzacio_jugador: Optional[str] = Field(
        default=None,
        description="ID of the scenario where the player is currently located."
    )