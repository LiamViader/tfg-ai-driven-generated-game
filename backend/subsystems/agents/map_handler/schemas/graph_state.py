from typing import Dict, List, Optional, Any, Annotated, Sequence, Literal, Set
from pydantic import BaseModel, Field
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator
# El '.' significa "desde el directori actual (schemas)"
from core_game.map.schemas import ScenarioModel, Direction, OppositeDirections
from subsystems.agents.utils.schemas import ToolLog


class MapGraphState(BaseModel):
    # Context and objectives
    map_foundational_lore_document: str = Field(default="", description="Narrative background and context of the world—its lore, themes, key story elements, etc— it is the seed used to create the world.")
    map_recent_operations_summary: str = Field(default="", description="Operations applied to the world by other agents before map agent")
    map_relevant_entity_details: str = Field(default="", description="Relevant entity details that could be usefull for the agent to achieve its task")
    map_additional_information: str = Field(default="", description="Additional context for the agent to achieve its objective")

    map_rules_and_constraints: List[str] = Field(default_factory=list, description="Explicit world-building rules or design constraints that must be respected when constructing or validating the map. These can include logical requirements (e.g., 'an exterior scenario connected to an interior one must feature a visible transition like a door or gate') or aesthetic guidelines that ensure internal consistency and visual coherence across the world.")
    map_current_objective: str = Field(default="", description="The high-level textual goal for the current map generation/modification task. Would be used for the validation agent too.")
    map_other_guidelines: str = Field(default="", description="Other guidelines for the map generation that should be met. Less strict than current objective. Will not be used by validation agent")
    map_initial_summary: str = Field(default="", description="Initial summary of the map when starting the workflow")

    # --- flux control ---
    map_max_retries: int = Field(default=1, description="Max retries of the whole process if validation fails")
    map_current_try: int = Field(default=1, description="Current try of the whole process")
    

    # --- Executor Agent memo ---
    map_executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages holding intermediate steps. For the Executor agent")
    map_current_executor_iteration: int = Field(default=0, description="Current iteration the react cycle is on")
    map_max_executor_iterations: int = Field(default=6, description="Max iterations of the react cycle before finishing")
    map_task_finalized_by_agent: bool = Field(default=False,description="A flag indicating whether the task was finalized by the agent")
    map_task_finalized_justification: Optional[str] = Field(default=None,description="A string of the justification provided by the agent who finalized the map")
    map_executor_applied_operations_log: Annotated[Sequence[ToolLog], operator.add] = Field(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, by the executor agent including 'tool_called', 'success', 'message'.")

    # --- Validation Agent memo ---
    map_max_validation_iterations: int = Field(default=3, description="Max iterations of the react validation cycle before finishing")
    map_current_validation_iteration: int = Field(default=0, description="Current iteration the react validation cycle is on")
    map_executor_agent_relevant_logs: str = Field(default="",description="Formated string holding the relevant executing agent logs and observation for the validator agent context")
    map_validation_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages holding intermediate steps. For the Validation agent")
    map_agent_validation_conclusion_flag: bool = Field(default=False,description="A flag indicating whether the validation agent said the map met all criteria")
    map_agent_validation_assessment_reasoning: str = Field(default="", description="Reasoning from agent of why the validation he gave.")
    map_agent_validation_suggested_improvements: str = Field(default="", description="Suggested improvements if the validation agent said map didnt meet criteria.")
    map_agent_validated: bool = Field(default=False,description="A flag indicating whether the validation agent gave a validation yet")
    map_validator_applied_operations_log: Annotated[Sequence[ToolLog], operator.add] = Field(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, by the validator agent including 'tool_called', 'success', 'message'.")

    # --- Finalizing ---
    map_task_succeeded_final: bool = Field(default=False, description="Flag indicating wether the agent succeeded on the task at the end of the process")

    #shared with all other agents
    logs_field_to_update:  str = Field(default="logs", description="Name of the field in the state where tool-generated logs should be appended")
    messages_field_to_update: str = Field(default="messages", description="Name of the field in the state where tool-generated messages should be appended")

    @staticmethod
    def get_opposite_direction(direction: Direction) -> Direction:
        """Helper method to get the opposite of a given direction."""
        return OppositeDirections[direction]