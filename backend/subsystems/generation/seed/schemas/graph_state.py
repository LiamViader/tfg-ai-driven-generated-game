import operator
from typing import Sequence, List
from typing_extensions import Annotated
from typing import Dict, List, Optional, Any, Annotated, Sequence
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from core_game.narrative.schemas import NarrativeStructureTypeModel
from utils.progress_tracker import ProgressTracker
class SeedGenerationGraphState(BaseModel):
    """
    Manages the state of the seed generation for the game.
    """

    initial_prompt: str = Field(..., description="User's initial prompt.")

    #REFINING PROMPT
    refined_prompt: str = Field(default="", description="User's refined prompt.")
    refined_prompt_desired_word_length: int = Field(default=1000, description="Desired word length for the refined prompt.")
    refine_generation_prompt_attempts: int = Field(default=0, description="Current attempt of refining the prompt.")
    refine_generation_prompt_max_attempts: int = Field(default=3, description="Max attempts for refining the prompt.")
    refine_generation_prompt_error_message: str = Field(default="", description="Error raised while trying to refine the prompt.")

    #MAIN GOAL
    main_goal: str = Field(default="",description="Main goal that gives direction to the player in the narrative.")
    generate_main_goal_attempts: int = Field(default=0,description="Current attempt of generating main goal")
    generate_main_goal_max_attempts: int = Field(default=3,description="Max attemps for generating the main goal")
    generate_main_goal_error_message: str = Field(default="", description="Error raised while trying to generate main goal")

    # NARRATIVE STRUCTURE SELECTION
    structure_selection_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages for the structure selection agent")
    current_structure_selection_iteration: int = Field(default=0, description="Current iteration in the structure selection process")
    max_structure_selection_reason_iterations: int = Field(default=4, description="Maximum iterations to reason to select a structure")
    max_structure_forced_selection_iterations: int = Field(default=3, description="Maximum attempts to select a structure")
    selected_structure: Optional[NarrativeStructureTypeModel] = Field(default=None, description="Narrative structure selected by the agent")
    structure_selection_justification: Optional[str] = Field(default=None, description="Justification of why the selected structure was chosen")

    seed_progress_tracker: Optional[ProgressTracker] = Field(
        default=None,
        description="Hierarchical tracker for managing nested progress across graphs/subgraphs."
    )

    #shared with other agents
    finalized_with_success: bool = Field(
        default=False,
        description="Indicates whether this process finalized with success."
    )
    class Config:
        arbitrary_types_allowed = True
