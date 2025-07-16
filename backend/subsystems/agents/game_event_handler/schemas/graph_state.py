from typing import List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from subsystems.agents.utils.schemas import ToolLog
from subsystems.agents.utils.logs import log_reducer
from utils.progress_tracker import ProgressTracker


class GameEventGraphState(BaseModel):
    """Holds context and working memory for the game event agent."""

    # Context and objectives
    events_foundational_lore_document: str = Field(
        default="",
        alias="events_global_narrative_context",
    )
    events_recent_operations_summary: str = Field(default="")
    events_relevant_entity_details: str = Field(default="")
    events_additional_information: str = Field(default="")

    events_rules_and_constraints: List[str] = Field(default_factory=list)
    events_current_objective: str = Field(default="")
    events_other_guidelines: str = Field(default="")
    events_initial_summary: str = Field(default="")

    # Flow control
    events_max_retries: int = Field(default=1)
    events_current_try: int = Field(default=0)

    # Executor agent
    events_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    events_current_executor_iteration: int = Field(default=0)
    events_max_executor_iterations: int = Field(default=6)
    events_task_finalized_by_agent: bool = Field(default=False)
    events_task_finalized_justification: Optional[str] = Field(default=None)
    events_executor_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    # Validation agent
    events_max_validation_iterations: int = Field(default=3)
    events_current_validation_iteration: int = Field(default=0)
    events_executor_agent_relevant_logs: str = Field(default="")
    events_validation_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    events_agent_validation_conclusion_flag: bool = Field(default=False)
    events_agent_validation_assessment_reasoning: str = Field(default="")
    events_agent_validation_suggested_improvements: str = Field(default="")
    events_agent_validated: bool = Field(default=False)
    events_validator_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    # Finalizing
    events_task_succeeded_final: bool = Field(default=False)

    events_progress_tracker: Optional[ProgressTracker] = Field(
        default=None,
    )

    # Shared fields
    logs_field_to_update: str = Field(default="logs")
    messages_field_to_update: str = Field(default="messages")

    class Config:
        arbitrary_types_allowed = True
