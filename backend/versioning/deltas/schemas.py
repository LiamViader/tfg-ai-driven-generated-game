from pydantic import BaseModel, Field
from typing import Dict, List, Any

class ChangeDetailModel(BaseModel, extra="allow"):
    """Represents a change from one value to another."""
    old: Any
    new: Any

class ConnectionDiffModel(BaseModel):
    """Detailed differences for a scenario's connections."""
    added: Dict[str, Any] = Field(default_factory=dict)
    removed: Dict[str, Any] = Field(default_factory=dict)
    changed: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class ScenarioDiffModel(BaseModel):
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    modified: List[str] = Field(default_factory=list)
    modified_visual_info: Dict[str, Dict[str, ChangeDetailModel]] = Field(default_factory=dict)
    modified_connections: Dict[str, ConnectionDiffModel] = Field(default_factory=dict)

# Modelo para los cambios en escenarios
class CharacterDiffModel(BaseModel):
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    modified: List[str] = Field(default_factory=list)
    modified_visual_info: Dict[str, Dict[str, ChangeDetailModel]] = Field(default_factory=dict)
    modified_location: Dict[str, ChangeDetailModel] = Field(default_factory=dict)

# Modelo principal que engloba todo el resultado del diff
class DiffResultModel(BaseModel):
    scenarios: ScenarioDiffModel
    characters: CharacterDiffModel
