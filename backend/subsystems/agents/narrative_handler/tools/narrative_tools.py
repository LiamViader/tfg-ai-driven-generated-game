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
    description: str = Field(
        ..., 
        description="The 'creative brief' for this beat. A detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )
    priority: int = Field(
        10, 
        description="Sets the execution priority for this beat within its stage. Higher numbers are executed sooner. Use this to order events logically."
    )

class ToolCreateFailureConditionWithBeatsArgs(InjectedToolContext):
    condition_description: str = Field(
        ...,
        description="The high-level description for the overall Failure Condition. e.g., 'The player is exposed as an impostor'; 'The heist alarm is triggered'."
    )
    beat_description_risk_30: str = Field(
        ...,
        description="The creative brief for the beat that triggers at 30 risk. Should describe the 'early warning' or initial complication of the failure path. Detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )
    beat_description_risk_60: str = Field(
        ...,
        description="The creative brief for the beat that triggers at 60 risk. Should describe a 'significant escalation' of the failure condition. Detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )
    beat_description_risk_100: str = Field(
        ...,
        description="The creative brief for the beat that triggers at 100 risk. Should describe the 'final, game-over climax' of this failure path. Detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )

class ToolAddRiskTriggeredBeatArgs(InjectedToolContext):
    condition_id: str = Field(
        ...,
        description="The ID of the `FailureCondition` to which this beat will be linked."
    )
    trigger_risk_level: int = Field(
        ..., 
        ge=0, 
        le=100,
        description="The risk percentage (0-100) at which this narrative beat becomes active and is added to the active beats list."
    )
    description: str = Field(
        ..., 
        description="The 'creative brief' for this beat. A detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )

class ToolSetFailureRiskLevelArgs(InjectedToolContext):
    condition_id: str = Field(
        ...,
        description="The ID of the `FailureCondition` whose risk level is being updated."
    )
    risk_level: int = Field(
        ..., 
        ge=0, 
        le=100,
        description="The new risk value (0-100) to set for the specified failure condition."
    )

class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str = Field(
        ...,
        description="A detailed justification explaining why the current narrative state fully satisfies the objective and is ready to be finalized."
    )

class ToolValidateSimulatedNarrativeArgs(InjectedToolContext):
    does_narrative_meet_criteria: bool = Field(
        ...,
        description="Set to 'true' if the narrative fulfills all objectives and constraints, 'false' otherwise."
    )
    assessment_reasoning: str = Field(
        ...,
        description="A detailed, step-by-step explanation of your reasoning for the 'true' or 'false' assessment."
    )
    suggested_improvements: str | None = Field(
        None,
        description="If 'false', provide specific, actionable suggestions for what the other agent should do next to fix the narrative."
    )

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
    """Creates and adds a new beat to the game's *current* narrative stage. Use this to create events that progress the main plot towards the ultimate 'main_goal'. The beat's description should be a clear 'creative brief'. Beats should match the current stage description. The added beat will be on pending status"""
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
    """Creates and adds a new beat to the game's *next* narrative stage. Use this to set up future events that will progress the main plot towards the ultimate 'main_goal' after the current stage is complete.  Beats should match the next stage description. The added beat will be on pending status"""
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

@tool(args_schema=ToolCreateFailureConditionWithBeatsArgs)
def create_failure_condition_with_beats(
    condition_description: str,
    beat_description_risk_30: str,
    beat_description_risk_60: str,
    beat_description_risk_100: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Creates a new, trackable failure condition AND simultaneously attaches the three mandatory risk-triggered beats at 30%, 60%, and 100% risk. This is the primary tool for creating failure paths."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    
    try:
        fc = FailureConditionModel(
            description=condition_description,
            is_active=False,
            risk_level=0,
        )
        simulated_state.add_failure_condition(fc)

        beats_info = [
            (beat_description_risk_30, 30),
            (beat_description_risk_60, 60),
            (beat_description_risk_100, 100)
        ]

        for desc, risk_level in beats_info:
            beat = NarrativeBeatModel(
                description=desc,
                priority=risk_level, 
                origin="FAILURE_CONDITION",
                status="PENDING",
            )
            rtb = RiskTriggeredBeats(
                trigger_risk_level=risk_level,
                deactivate_risk_level=risk_level -1 if risk_level > 0 else 0,
                beats=[beat],
            )
            simulated_state.add_risk_triggered_beats(fc.id, rtb)

        message = f"Failure condition '{fc.id}' created successfully with 3 mandatory beats at risks 30, 60, and 100."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_failure_condition_with_beats", args, False, success, message)],
        messages_field_to_update: [ToolMessage(message, tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolAddRiskTriggeredBeatArgs)
def add_risk_triggered_beat(condition_id: str, trigger_risk_level: int,
                            description: str,
                            messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                            logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                            tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Creates and links a new risk triggered beat to a specific failure condition. This beat will automatically activate when the condition's risk level reaches the 'trigger_risk_level'."""
    args = extract_tool_args(locals())
    beat = NarrativeBeatModel(
        description=description,
        priority=10,
        origin="FAILURE_CONDITION",
        status="PENDING",
    )
    rtb = RiskTriggeredBeats(
        trigger_risk_level=trigger_risk_level,
        deactivate_risk_level=trigger_risk_level-1,
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
    """Updates the current risk percentage (0-100) of a specific failure condition. This can trigger or deactivate associated beats."""
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
    create_failure_condition_with_beats, 
    add_risk_triggered_beat,
    set_failure_risk_level,
    finalize_simulation,
]

VALIDATIONTOOLS = [
    validate_simulated_narrative,
]

QUERYTOOLS = [

]
