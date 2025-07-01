from typing import Annotated
from pydantic import Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from core_game.narrative.schemas import (
    NarrativeBeatModel,
    FailureConditionModel,
    RiskTriggeredBeats,
)

class ToolAddBeatArgs(InjectedToolContext):
    description: str = Field(..., description="Description of the beat")
    priority: int = Field(10, description="Beat priority")

class ToolCreateFailureConditionArgs(InjectedToolContext):
    description: str = Field(..., description="Description")

class ToolAddRiskTriggeredBeatArgs(InjectedToolContext):
    condition_id: str = Field(..., description="Failure condition id")
    trigger_risk_level: int = Field(..., ge=0, le=100)
    deactivate_risk_level: int = Field(..., ge=0, le=100)
    description: str = Field(..., description="Beat description")
    priority: int = Field(10)

class ToolSetFailureRiskLevelArgs(InjectedToolContext):
    condition_id: str = Field(...)
    risk_level: int = Field(..., ge=0, le=100)

class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str

class ToolValidateSimulatedNarrativeArgs(InjectedToolContext):
    does_narrative_meet_criteria: bool
    assessment_reasoning: str
    suggested_improvements: str | None = None

class ToolGetStructureDetailsArgs(InjectedToolContext):
    pass


@tool(args_schema=ToolAddBeatArgs)
def add_beat_current_stage(
    description: str,
    priority: int,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Add a narrative beat to the current stage."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(
        description=description,
        priority=priority,
        origin="NARRATIVE_STAGE",
        status="PENDING",
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        stage_index = simulated_state.get_current_stage_index()
        simulated_state.add_narrative_beat(stage_index, beat)
        message = f"Beat '{beat.id}' added to current stage"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_beat_current_stage", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolAddBeatArgs)
def add_beat_next_stage(
    description: str,
    priority: int,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Add a narrative beat to the next stage."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(
        description=description,
        priority=priority,
        origin="NARRATIVE_STAGE",
        status="PENDING",
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        stage_index = simulated_state.get_next_stage_index()
        simulated_state.add_narrative_beat(stage_index, beat)
        message = f"Beat '{beat.id}' added to next stage"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_beat_next_stage", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateFailureConditionArgs)
def create_failure_condition(description: str,
                             messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                             logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                             tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Create a new failure condition."""
    args = extract_tool_args(locals())
    fc = FailureConditionModel(
        description=description,
        is_active=False,
        risk_level=0,
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.add_failure_condition(fc)
        message = f"Failure condition '{fc.id}' created"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_failure_condition", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolAddRiskTriggeredBeatArgs)
def add_risk_triggered_beat(condition_id: str, trigger_risk_level: int, deactivate_risk_level: int,
                            description: str, priority: int,
                            messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                            logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                            tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Associate beats to a failure condition triggered at certain risk level."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(
        description=description,
        priority=priority,
        origin="FAILURE_CONDITION",
        status="PENDING",
    )
    rtb = RiskTriggeredBeats(
        trigger_risk_level=trigger_risk_level,
        deactivate_risk_level=deactivate_risk_level,
        beats=[beat],
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.add_risk_triggered_beats(condition_id, rtb)
        message = f"Risk triggered beat '{beat.id}' added"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_risk_triggered_beat", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolSetFailureRiskLevelArgs)
def set_failure_risk_level(condition_id: str, risk_level: int,
                           messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                           logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                           tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Set the risk level of a failure condition."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.set_failure_risk_level(condition_id, risk_level)
        message = f"Risk level for '{condition_id}' set to {risk_level}"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("set_failure_risk_level", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(justification: str,
                        messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                        logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                        tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Finalize the narrative executor."""
    args = extract_tool_args(locals())
    message = justification
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
        "narrative_task_finalized_by_agent": True,
        "narrative_task_finalized_justification": justification,
    })


@tool(args_schema=ToolGetStructureDetailsArgs)
def get_narrative_structure_details(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) Return all stages with descriptions, beats, and current-stage marker."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        details = simulated_state.get_narrative_structure_details()
        message = details
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("get_narrative_structure_details", args, True, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolValidateSimulatedNarrativeArgs)
def validate_simulated_narrative(messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                                 logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                                 tool_call_id: Annotated[str, InjectedToolCallId],
                                 does_narrative_meet_criteria: bool,
                                 assessment_reasoning: str,
                                 suggested_improvements: str | None = None) -> Command:
    """Validate the narrative after execution."""
    args = extract_tool_args(locals())
    if not suggested_improvements:
        suggested_improvements = ""
    if does_narrative_meet_criteria:
        message = f"Narrative meets criteria. Reason: {assessment_reasoning}"
    else:
        message = f"Narrative does not meet criteria. Reason: {assessment_reasoning}. Suggestions: {suggested_improvements}"
    return Command(update={
        logs_field_to_update: [get_log_item("validate_simulated_narrative", args, False, True, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
        "narrative_agent_validated": True,
        "narrative_agent_validation_conclusion_flag": does_narrative_meet_criteria,
        "narrative_agent_validation_assessment_reasoning": assessment_reasoning,
        "narrative_agent_validation_suggested_improvements": suggested_improvements,
    })

EXECUTORTOOLS = [
    add_beat_current_stage,
    add_beat_next_stage,
    create_failure_condition,
    add_risk_triggered_beat,
    set_failure_risk_level,
    get_narrative_structure_details,
    finalize_simulation,
]

VALIDATIONTOOLS = [
    get_narrative_structure_details,
    validate_simulated_narrative,
]

QUERYTOOLS = [
    get_narrative_structure_details,
]
