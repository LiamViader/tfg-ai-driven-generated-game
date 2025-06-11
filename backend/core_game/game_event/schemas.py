from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field

class GameEventModel(BaseModel):
    id: str = Field(...,description="id of the game event")