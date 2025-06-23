
from typing import Dict, List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator

from subsystems.agents.utils.schemas import ToolLog

class CharacterGraphState(BaseModel):
    """Holds context and working memory for the character agent."""

    characters_global_narrative_context: str = Field(..., description="Narrative context provided to the agent to operate.")
    characters_rules_and_constraints: List[str] = Field(..., description="Rules or constraints for the character agent to follow.")
    characters_current_objective: str = Field(..., description="Current objective")
    characters_other_guidelines: str = Field(..., description="Additional softer guidelines")
    characters_initial_summary: str = Field(default="", description="Initial summary of the cast")

    characters_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages holding intermediate steps. For the Executor agent")
    characters_current_executor_iteration: int = Field(default=0, description="Current iteration the react cycle is on")
    characters_max_executor_iterations: int = Field(..., description="Maximum iterations for the executor to achieve the objective.")
    characters_executor_applied_operations_log: Annotated[Sequence[ToolLog], operator.add] = Field(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, by the executor agent including 'tool_called', 'success', 'message'.")

    characters_task_finalized_by_agent: bool = Field(default=False, description="Flag set when the agent finalizes the task")
    characters_task_finalized_justification: Optional[str] = Field(default=None, description="Justification provided when finalizing the task")

    #shared with all other agents
    logs_field_to_update:  str = Field(default="logs", description="Name of the field in the state where tool-generated logs should be appended")
    messages_field_to_update: str = Field(default="messages", description="Name of the field in the state where tool-generated messages should be appended")
