from typing import Annotated
from pydantic import BaseModel, Field
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

class ToolAddNarrativeBeatArgs(InjectedToolContext):
    stage_index: int = Field(..., description="Stage index to add the beat")
    beat_id: str = Field(..., description="Unique id for the beat")
    description: str = Field(..., description="Description of the beat")
    priority: int = Field(10, description="Beat priority")

class ToolCreateFailureConditionArgs(InjectedToolContext):
    condition_id: str = Field(..., description="Failure condition id")
    description: str = Field(..., description="Description")

class ToolAddRiskTriggeredBeatArgs(InjectedToolContext):
    condition_id: str = Field(..., description="Failure condition id")
    trigger_risk_level: int = Field(..., ge=0, le=100)
    deactivate_risk_level: int = Field(..., ge=0, le=100)
    beat_id: str = Field(..., description="Beat id")
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

@tool(args_schema=ToolAddNarrativeBeatArgs)
def add_narrative_beat(stage_index: int, beat_id: str, description: str, priority: int,
                       messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                       logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                       tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Add a narrative beat to a stage."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(id=beat_id, description=description, priority=priority, origin="NARRATIVE_STAGE", status="PENDING")
    SimulatedGameStateSingleton.get_instance().add_narrative_beat(stage_index, beat)
    message = f"Beat '{beat_id}' added"
    return Command(update={
        logs_field_to_update: [get_log_item("add_narrative_beat", args, False, True, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateFailureConditionArgs)
def create_failure_condition(condition_id: str, description: str,
                             messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                             logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                             tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Create a new failure condition."""
    args = extract_tool_args(locals())
    fc = FailureConditionModel(id=condition_id, description=description, is_active=False, risk_level=0)
    SimulatedGameStateSingleton.get_instance().add_failure_condition(fc)
    message = f"Failure condition '{condition_id}' created"
    return Command(update={
        logs_field_to_update: [get_log_item("create_failure_condition", args, False, True, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolAddRiskTriggeredBeatArgs)
def add_risk_triggered_beat(condition_id: str, trigger_risk_level: int, deactivate_risk_level: int,
                            beat_id: str, description: str, priority: int,
                            messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                            logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                            tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Associate beats to a failure condition triggered at certain risk level."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(id=beat_id, description=description, priority=priority, origin="FAILURE_CONDITION", status="PENDING")
    rtb = RiskTriggeredBeats(trigger_risk_level=trigger_risk_level, deactivate_risk_level=deactivate_risk_level, beats=[beat])
    SimulatedGameStateSingleton.get_instance().add_risk_triggered_beats(condition_id, rtb)
    message = f"Risk triggered beat '{beat_id}' added"
    return Command(update={
        logs_field_to_update: [get_log_item("add_risk_triggered_beat", args, False, True, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolSetFailureRiskLevelArgs)
def set_failure_risk_level(condition_id: str, risk_level: int,
                           messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                           logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                           tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Set the risk level of a failure condition."""
    args = extract_tool_args(locals())
    SimulatedGameStateSingleton.get_instance().set_failure_risk_level(condition_id, risk_level)
    message = f"Risk level for '{condition_id}' set to {risk_level}"
    return Command(update={
        logs_field_to_update: [get_log_item("set_failure_risk_level", args, False, True, message)],
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
    add_narrative_beat,
    create_failure_condition,
    add_risk_triggered_beat,
    set_failure_risk_level,
    finalize_simulation,
]

VALIDATIONTOOLS = [
    validate_simulated_narrative,
]
