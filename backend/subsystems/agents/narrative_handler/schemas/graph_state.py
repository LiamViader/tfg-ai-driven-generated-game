from typing import List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from subsystems.agents.utils.schemas import ToolLog
from subsystems.agents.utils.logs import log_reducer
from utils.progress_tracker import ProgressTracker

class NarrativeGraphState(BaseModel):
    """Holds context and working memory for the narrative agent."""
    narrative_foundational_lore_document: str = Field(default="", alias="narrative_global_narrative_context")
    narrative_recent_operations_summary: str = Field(default="")
    narrative_relevant_entity_details: str = Field(default="")
    narrative_additional_information: str = Field(default="")

    narrative_rules_and_constraints: List[str] = Field(default_factory=list)
    narrative_current_objective: str = Field(default="")
    narrative_other_guidelines: str = Field(default="")
    narrative_initial_summary: str = Field(default="")

    narrative_max_retries: int = Field(default=1)
    narrative_current_try: int = Field(default=0)

    narrative_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    narrative_current_executor_iteration: int = Field(default=0)
    narrative_max_executor_iterations: int = Field(default=6)
    narrative_task_finalized_by_agent: bool = Field(default=False)
    narrative_task_finalized_justification: Optional[str] = Field(default=None)
    narrative_executor_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    narrative_max_validation_iterations: int = Field(default=3)
    narrative_current_validation_iteration: int = Field(default=0)
    narrative_executor_agent_relevant_logs: str = Field(default="")
    narrative_validation_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    narrative_agent_validation_conclusion_flag: bool = Field(default=False)
    narrative_agent_validation_assessment_reasoning: str = Field(default="")
    narrative_agent_validation_suggested_improvements: str = Field(default="")
    narrative_agent_validated: bool = Field(default=False)
    narrative_validator_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    narrative_task_succeeded_final: bool = Field(default=False)

    narrative_progress_tracker: Optional[ProgressTracker] = Field(
        default=None,
    )

    logs_field_to_update: str = Field(default="logs")
    messages_field_to_update: str = Field(default="messages")

    class Config:
        arbitrary_types_allowed = True