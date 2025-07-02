from typing import Annotated, Optional

from pydantic import Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from .helpers import get_observation


class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str = Field(..., description="Explanation of why the events meet the objective")


class ToolValidateSimulatedGameEventsArgs(InjectedToolContext):
    does_game_events_meet_criteria: bool = Field(..., description="True if events meet the objective")
    assessment_reasoning: str = Field(..., description="Reasoning behind the validation outcome")
    suggested_improvements: Optional[str] = Field(
        default=None,
        description="Suggestions on how to improve if validation failed",
    )


@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Finalize the game events executor."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    message = justification
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation("finalize_simulation", True, message),
                tool_call_id=tool_call_id,
            )
        ],
        "events_task_finalized_by_agent": True,
        "events_task_finalized_justification": justification,
    })


@tool(args_schema=ToolValidateSimulatedGameEventsArgs)
def validate_simulated_game_events(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    does_game_events_meet_criteria: bool,
    assessment_reasoning: str,
    suggested_improvements: Optional[str] = None,
) -> Command:
    """Validate the simulated game events."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    if not suggested_improvements:
        suggested_improvements = ""
    if does_game_events_meet_criteria:
        message = f"Game events meet criteria. Reason: {assessment_reasoning}"
    else:
        message = (
            f"Game events do not meet criteria. Reason: {assessment_reasoning}. Suggestions: {suggested_improvements}"
        )
    return Command(update={
        logs_field_to_update: [
            get_log_item("validate_simulated_game_events", args, False, True, message)
        ],
        messages_field_to_update: [
            ToolMessage(
                get_observation("validate_simulated_game_events", True, message),
                tool_call_id=tool_call_id,
            )
        ],
        "events_agent_validated": True,
        "events_agent_validation_conclusion_flag": does_game_events_meet_criteria,
        "events_agent_validation_assessment_reasoning": assessment_reasoning,
        "events_agent_validation_suggested_improvements": suggested_improvements,
    })


EXECUTORTOOLS = [finalize_simulation]
VALIDATIONTOOLS = [validate_simulated_game_events]
