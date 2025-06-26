
from typing import List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator

from subsystems.agents.utils.schemas import ToolLog
from subsystems.agents.utils.logs import log_reducer

class CharacterGraphState(BaseModel):
    """Holds context and working memory for the character agent."""

    # Context and objectives
    characters_foundational_lore_document: str = Field(
        default="",
        alias="characters_global_narrative_context",
        description=(
            "Narrative background and context of the world—its lore, themes, key "
            "story elements, etc— it is the seed used to create the world."
        ),
    )
    characters_recent_operations_summary: str = Field(
        default="",
        description="Operations applied to the world by other agents before character agent",
    )
    characters_relevant_entity_details: str = Field(
        default="",
        description="Relevant entity details that could be useful for the agent to achieve its task",
    )
    characters_additional_information: str = Field(
        default="",
        description="Additional context for the agent to achieve its objective",
    )

    characters_rules_and_constraints: List[str] = Field(
        default_factory=list,
        description="Explicit design rules or constraints that must be respected",
    )
    characters_current_objective: str = Field(
        default="",
        description="The high-level textual goal for the current character generation/modification task.",
    )
    characters_other_guidelines: str = Field(
        default="",
        description="Other guidelines for the character generation that should be met. Less strict than current objective.",
    )
    characters_initial_summary: str = Field(
        default="",
        description="Initial summary of the cast when starting the workflow",
    )

    # --- flux control ---
    characters_max_retries: int = Field(
        default=1, description="Max retries of the whole process if validation fails"
    )
    characters_current_try: int = Field(
        default=1, description="Current try of the whole process"
    )

    # --- Executor Agent memo ---
    characters_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Messages holding intermediate steps. For the Executor agent",
    )
    characters_current_executor_iteration: int = Field(
        default=0, description="Current iteration the react cycle is on"
    )
    characters_max_executor_iterations: int = Field(
        default=6, description="Max iterations of the react cycle before finishing"
    )
    characters_task_finalized_by_agent: bool = Field(
        default=False, description="A flag indicating whether the task was finalized by the agent"
    )
    characters_task_finalized_justification: Optional[str] = Field(
        default=None,
        description="A string of the justification provided by the agent who finalized the characters",
    )
    characters_executor_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(
        default_factory=list,
        description="A chronological log of all tool-based operations applied to the simulated characters, by the executor agent including 'tool_called', 'success', 'message'.",
    )

    # --- Validation Agent memo ---
    characters_max_validation_iterations: int = Field(
        default=3,
        description="Max iterations of the react validation cycle before finishing",
    )
    characters_current_validation_iteration: int = Field(
        default=0, description="Current iteration the react validation cycle is on"
    )
    characters_executor_agent_relevant_logs: str = Field(
        default="",
        description="Formatted string holding the relevant executing agent logs and observation for the validator agent context",
    )
    characters_validation_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(
        default_factory=list,
        description="Messages holding intermediate steps. For the Validation agent",
    )
    characters_agent_validation_conclusion_flag: bool = Field(
        default=False,
        description="A flag indicating whether the validation agent said the characters met all criteria",
    )
    characters_agent_validation_assessment_reasoning: str = Field(
        default="",
        description="Reasoning from agent of why the validation he gave.",
    )
    characters_agent_validation_suggested_improvements: str = Field(
        default="",
        description="Suggested improvements if the validation agent said the characters didn't meet criteria.",
    )
    characters_agent_validated: bool = Field(
        default=False,
        description="A flag indicating whether the validation agent gave a validation yet",
    )
    characters_validator_applied_operations_log: Annotated[Sequence[ToolLog], log_reducer] = Field(
        default_factory=list,
        description="A chronological log of all tool-based operations applied to the simulated characters, by the validator agent including 'tool_called', 'success', 'message'.",
    )

    # --- Finalizing ---
    characters_task_succeeded_final: bool = Field(
        default=False,
        description="Flag indicating whether the agent succeeded on the task at the end of the process",
    )

    # shared with all other agents
    logs_field_to_update: str = Field(
        default="logs",
        description="Name of the field in the state where tool-generated logs should be appended",
    )
    messages_field_to_update: str = Field(
        default="messages",
        description="Name of the field in the state where tool-generated messages should be appended",
    )

