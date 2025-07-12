import operator
from typing import Sequence, List
from typing_extensions import Annotated

from pydantic import BaseModel, Field
from subsystems.generation.refinement_loop.schemas.pipeline_config import PipelineConfig
from subsystems.agents.character_handler.schemas.graph_state import CharacterGraphState
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.agents.relationship_handler.schemas.graph_state import RelationshipGraphState
from subsystems.agents.narrative_handler.schemas.graph_state import NarrativeGraphState
from subsystems.agents.game_event_handler.schemas.graph_state import GameEventGraphState
from subsystems.summarize_agent_logs.schemas.graph_state import SummarizeLogsGraphState
from subsystems.agents.utils.schemas import AgentLog
class RefinementLoopGraphState(CharacterGraphState, MapGraphState, RelationshipGraphState, NarrativeGraphState, GameEventGraphState, SummarizeLogsGraphState):
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

    changelog_old_operations_summary: str = Field(default="", description="Old operations that are out of the window summarized")

    last_step_succeeded: bool = Field(default=False, description="Whether the las step succeeded")

    refinement_foundational_world_info: str = Field(default="", description="Foundational info about the world that will be passed to the agents")

    #Shared with other agents
    refinement_pass_changelog: Annotated[Sequence[AgentLog], operator.add] = Field(
        default_factory=list,
        description="A log that accumulates the summary or outcome of each agent's operation in every pass. The 'operator.add' ensures that new log entries are appended, creating a complete history of the generation process."
    )

    finalized_with_success: bool = Field(
        default=False,
        description="Indicates whether this process finalized with success."
    )

