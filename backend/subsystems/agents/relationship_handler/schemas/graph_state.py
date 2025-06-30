from typing import List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from subsystems.agents.utils.schemas import ToolLog
from subsystems.agents.utils.logs import log_reducer

class RelationshipGraphState(BaseModel):
    """Holds context and working memory for the relationship agent."""

    # Context and objectives
    relationships_foundational_lore_document: str = Field(default="", alias="relationships_global_narrative_context")
    relationships_recent_operations_summary: str = Field(default="")
    relationships_relevant_entity_details: str = Field(default="")
    relationships_additional_information: str = Field(default="")

    relationships_rules_and_constraints: List[str] = Field(default_factory=list)
    relationships_current_objective: str = Field(default="")
    relationships_other_guidelines: str = Field(default="")
    relationships_initial_summary: str = Field(default="")

    # flow control
    relationships_max_retries: int = Field(default=1)
    relationships_current_try: int = Field(default=1)

    # executor
    relationships_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    relationships_current_executor_iteration: int = Field(default=0)
    relationships_max_executor_iterations: int = Field(default=6)
    relationships_task_finalized_by_agent: bool = Field(default=False)
    relationships_task_finalized_justification: Optional[str] = Field(default=None)
    relationships_executor_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    # validator
    relationships_max_validation_iterations: int = Field(default=3)
    relationships_current_validation_iteration: int = Field(default=0)
    relationships_executor_agent_relevant_logs: str = Field(default="")
    relationships_validation_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    relationships_agent_validation_conclusion_flag: bool = Field(default=False)
    relationships_agent_validation_assessment_reasoning: str = Field(default="")
    relationships_agent_validation_suggested_improvements: str = Field(default="")
    relationships_agent_validated: bool = Field(default=False)
    relationships_validator_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(default_factory=list)

    # final
    relationships_task_succeeded_final: bool = Field(default=False)

    # shared
    logs_field_to_update: str = Field(default="logs")
    messages_field_to_update: str = Field(default="messages")

