from pydantic import BaseModel, Field
from typing import Dict, List, Any, TypeVar

# Un tipo genérico para los detalles del cambio
T = TypeVar('T')

class ChangeDetailModel(BaseModel, extra='allow'):
    """Modelo genérico para representar un cambio de un valor antiguo a uno nuevo."""
    old: Any
    new: Any

# Modelo para los cambios en escenarios
class ScenarioDiffModel(BaseModel):
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    modified: List[str] = Field(default_factory=list)
    # Ahora usamos nuestro modelo específico para los detalles
    modified_visual_info: Dict[str, Dict[str, ChangeDetailModel]] = Field(default_factory=dict)
    modified_connections: Dict[str, ChangeDetailModel] = Field(default_factory=dict)

# Modelo para los cambios en personajes
class CharacterDiffModel(BaseModel):
    added: List[str] = Field(default_factory=list)
    removed: List[str] = Field(default_factory=list)
    modified: List[str] = Field(default_factory=list)
    # Usamos el mismo modelo aquí
    modified_visual_info: Dict[str, Dict[str, ChangeDetailModel]] = Field(default_factory=dict)
    modified_location: Dict[str, ChangeDetailModel] = Field(default_factory=dict)

# Modelo principal que engloba todo el resultado del diff
class DiffResultModel(BaseModel):
    scenarios: ScenarioDiffModel
    characters: CharacterDiffModel