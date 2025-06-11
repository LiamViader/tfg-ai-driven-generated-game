from typing import Dict, List, Optional, Literal, Any, Union
from pydantic import BaseModel, Field, field_validator


class GameTimeModel(BaseModel):
    """Represents in-game time in a structured way."""
    total_minutes_elapsed: int = Field(0, description="Global counter of minutes elapsed since the start.")
    day: int = Field(1, description="The current day in the narrative.")
    hour: int = Field(8, description="The current hour (24h format).")
    minute: int = Field(0, description="The current minute.")
    