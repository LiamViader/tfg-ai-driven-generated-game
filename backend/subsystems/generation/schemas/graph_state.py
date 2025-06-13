from typing import Dict, List, Optional, Any, Annotated, Sequence
from pydantic import BaseModel, Field
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages




class GenerationGraphState(BaseModel):
    initial_prompt: str = Field(..., description="User's initial prompt.")
    refined_prompt: str = Field(default="", description="User's prompt after refinement.")

    #MAIN GOAL
    main_goal: str = Field(default="",description="Main goal that gives direction to the player in the narrative.")
    generate_main_goal_attempts: int = Field(default=0,description="Current attempt of generating main goal")
    generate_main_goal_max_attempts: int = Field(...,description="Max attemps for generating the main goal")
    generate_main_goal_error_message: str = Field(default="", description="Error raised while trying to generate main goal")

    # NARRATIVE STRUCTURE SELECTION
    selected_structure_type_id: str = Field(default="", description="ID of the chosen narrative structure type")
    selected_structure_type_name: str = Field(default="", description="Name of the chosen narrative structure type")
    structure_selection_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages for the structure selection agent")
    current_structure_selection_iteration: int = Field(default=0, description="Current iteration in the structure selection process")
    max_structure_selection_iterations: int = Field(default=3, description="Maximum attempts to select a structure")
