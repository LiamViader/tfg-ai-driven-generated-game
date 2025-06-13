from typing import Dict, List, Optional, Any, Annotated, Sequence
from pydantic import BaseModel, Field

class MainGoal(BaseModel):
    """The main goal for the player in the narrative game."""
    main_goal: str = Field(min_length=10,description="The actionable, open-ended main goal for the player.")