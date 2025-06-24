import operator
from typing import Sequence, List
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from subsystems.generation_pipeline.refinement_loop.schemas.pipeline_config import PipelineConfig
from subsystems.agents.character_handler.schemas.graph_state import CharacterGraphState
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.summarize_agent_logs.schemas.graph_state import SummarizeLogsGraphState

class RefinementLoopGraphState(CharacterGraphState, MapGraphState, SummarizeLogsGraphState):
    """
    Manages the state of the iterative N-pass enrichment loop.
    """

    refinement_pipeline_config: PipelineConfig = Field(
        ...,
        description="The configuration object that defines the sequence of agents and their objectives for each generation pass. This is the 'recipe' for the entire process."
    )

    refinement_current_pass: int = Field(
        default=0,
        description="A counter for the current enrichment pass. It starts at 0 and should be incremented by the graph's control logic before starting a new loop."
    )
    
    refinement_pass_changelog: Annotated[Sequence[str], operator.add] = Field(
        default_factory=list,
        description="A log that accumulates the summary or outcome of each agent's operation in every pass. The 'operator.add' ensures that new log entries are appended, creating a complete history of the generation process."
    )

    changelog_old_operations_summary: str = Field(default="", description="Old operations that are out of the window summarized")

    #Shared with other agents
    refined_prompt: str = Field(default="", description="User's refined prompt.")


