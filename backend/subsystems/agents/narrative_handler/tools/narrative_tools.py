from typing import Annotated, List
from pydantic import Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from .helpers import get_observation, _format_nested_dict
from core_game.narrative.schemas import (
    NarrativeBeatModel,
    FailureConditionModel,
    RiskTriggeredBeat,
)

class ToolAddBeatArgs(InjectedToolContext):
    name: str = Field(
        ...,
        description="Short name (7-15 words) summarizing the beat. If omitted the first words of the description will be used.",
    )
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
    beat_name_risk_30: str = Field(
        ...,
        description="Short name for the 30 risk beat. If omitted, the first words of the description will be used.",
    )
    beat_description_risk_30: str = Field(
        ...,
        description="The creative brief for the beat that triggers at 30 risk. Should describe the 'early warning' or initial complication of the failure path. Detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words)."
    )
    beat_name_risk_60: str = Field(
        ...,
        description="Short name for the 60 risk beat. If omitted, the first words of the description will be used.",
    )
    beat_description_risk_60: str = Field(
        ...,
        description="The creative brief for the beat that triggers at 60 risk. Should describe the escalating complication of the failure path. Detailed, self-contained description. Must clearly state the intent, key actions, and the criteria for the beat's resolution. This text will be used by another agent to generate final game content (dialogues, actions). (Approx. 100-150 words).",
    )
    beat_name_risk_100: str = Field(
        ...,
        description="Short name for the 100 risk beat. If omitted, the first words of the description will be used.",
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
    name: str = Field(
        ...,
        description="Short name for the beat. If omitted, the first words of the description will be used.",
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

class ToolGetBeatDetailsArgs(InjectedToolContext):
    beat_id: str = Field(..., description="ID of the narrative beat to inspect")

class ToolGetFailureConditionDetailsArgs(InjectedToolContext):
    condition_id: str = Field(..., description="ID of the failure condition")

class ToolListBeatsArgs(InjectedToolContext):
    pass

@tool(args_schema=ToolAddBeatArgs)
def add_beat_current_stage(
    name: str,
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
        name=name
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        stage_index = simulated_state.get_current_stage_index()
        simulated_state.add_narrative_beat(stage_index, beat)
        message = f"Beat {beat.id} with status {beat.status} added to current narrative stage"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_beat_current_stage", args, False, success, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "add_beat_current_stage",
                success,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
    })


@tool(args_schema=ToolAddBeatArgs)
def add_beat_next_stage(
    name: str,
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
        name=name
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        stage_index = simulated_state.get_next_stage_index()
        simulated_state.add_narrative_beat(stage_index, beat)
        message = f"Beat {beat.id} with status {beat.status} added to next narrative stage"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_beat_next_stage", args, False, success, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "add_beat_next_stage",
                success,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
    })

@tool(args_schema=ToolCreateFailureConditionWithBeatsArgs)
def create_failure_condition_with_beats(
    condition_description: str,
    beat_name_risk_30: str,
    beat_description_risk_30: str,
    beat_name_risk_60: str,
    beat_description_risk_60: str,
    beat_name_risk_100: str,
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
            (beat_name_risk_30, beat_description_risk_30, 30),
            (beat_name_risk_60, beat_description_risk_60, 60),
            (beat_name_risk_100, beat_description_risk_100, 100)
        ]
        beats: List[NarrativeBeatModel] = []
        for name, desc, risk_level in beats_info:
            beat = NarrativeBeatModel(
                description=desc,
                priority=risk_level, 
                origin="FAILURE_CONDITION",
                status="PENDING",
                name=name
            )
            rtb = RiskTriggeredBeat(
                trigger_risk_level=risk_level,
                deactivate_risk_level=risk_level -1 if risk_level > 0 else 0,
                beat=beat,
            )
            beats.append(beat)
            simulated_state.add_risk_triggered_beats(fc.id, rtb)

        message = f"Failure condition '{fc.id}' created successfully with {beats[0].id}: {beats[0].name} at risk 30, {beats[1].id}: {beats[1].name} at risk 60, and {beats[2].id}: {beats[2].name} at risk 100."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_failure_condition_with_beats", args, False, success, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "create_failure_condition_with_beats",
                success,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
    })

@tool(args_schema=ToolAddRiskTriggeredBeatArgs)
def add_risk_triggered_beat(condition_id: str, trigger_risk_level: int,
                            name: str,
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
        name=name
    )
    rtb = RiskTriggeredBeat(
        trigger_risk_level=trigger_risk_level,
        deactivate_risk_level=trigger_risk_level-1,
        beat=beat,
    )
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.add_risk_triggered_beats(condition_id, rtb)
        message = f"Risk triggered beat {beat.id}: {beat.name} added"
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("add_risk_triggered_beat", args, False, success, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "add_risk_triggered_beat",
                success,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
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
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "set_failure_risk_level",
                success,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
    })

@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(justification: str,
                        messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
                        logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
                        tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Finalize the narrative executor."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    message = justification
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "finalize_simulation",
                True,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
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
    simulated_state = SimulatedGameStateSingleton.get_instance()
    if not suggested_improvements:
        suggested_improvements = ""
    if does_narrative_meet_criteria:
        message = f"Narrative meets criteria. Reason: {assessment_reasoning}"
    else:
        message = f"Narrative does not meet criteria. Reason: {assessment_reasoning}. Suggestions: {suggested_improvements}"
    return Command(update={
        logs_field_to_update: [get_log_item("validate_simulated_narrative", args, False, True, message)],
        messages_field_to_update: [ToolMessage(
            get_observation(
                simulated_state.narrative_beats_count(),
                "validate_simulated_narrative",
                True,
                message,
            ),
            tool_call_id=tool_call_id,
        )],
        "narrative_agent_validated": True,
        "narrative_agent_validation_conclusion_flag": does_narrative_meet_criteria,
        "narrative_agent_validation_assessment_reasoning": assessment_reasoning,
        "narrative_agent_validation_suggested_improvements": suggested_improvements,
    })


@tool(args_schema=ToolGetBeatDetailsArgs)
def get_narrative_beat_details(
    beat_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) Get full details of a narrative beat by its ID."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    beat = simulated_state.get_narrative_beat(beat_id)
    if not beat:
        message = f"Beat with ID '{beat_id}' not found."
        success = False
    else:
        details = beat.model_dump()
        message = "\n" + "\n".join(_format_nested_dict(details))
        success = True
    return Command(update={
        logs_field_to_update: [get_log_item("get_narrative_beat_details", args, True, success, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_state.narrative_beats_count(), "get_narrative_beat_details", success, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolGetFailureConditionDetailsArgs)
def get_failure_condition_details(
    condition_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) Get details of a failure condition by its ID."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    fc = simulated_state.get_failure_condition(condition_id)
    if not fc:
        message = f"Failure condition '{condition_id}' not found."
        success = False
    else:
        details = fc.model_dump()
        message = "\n" + "\n".join(_format_nested_dict(details))
        success = True
    return Command(update={
        logs_field_to_update: [get_log_item("get_failure_condition_details", args, True, success, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_state.narrative_beats_count(), "get_failure_condition_details", success, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolListBeatsArgs)
def list_active_beats(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) List all currently active beats."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    beats = simulated_state.list_active_beats()
    if not beats:
        message = "No active beats."
    else:
        message = "\n".join(f"{b.id}: {b.name} [{b.status}]" for b in beats)
    return Command(update={
        logs_field_to_update: [get_log_item("list_active_beats", args, True, True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_state.narrative_beats_count(), "list_active_beats", True, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolListBeatsArgs)
def list_pending_beats(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) List pending beats from the main narrative only."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    beats = simulated_state.list_pending_beats_main()
    if not beats:
        message = "No pending beats."
    else:
        message = "\n".join(f"{b.id}: {b.name} [{b.status}]" for b in beats)
    return Command(update={
        logs_field_to_update: [get_log_item("list_pending_beats", args, True, True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_state.narrative_beats_count(), "list_pending_beats", True, message), tool_call_id=tool_call_id)
        ]
    })


@tool(args_schema=ToolListBeatsArgs)
def list_current_and_next_stage_beats(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY tool) List beats from the current and next narrative stages."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    current_beats = simulated_state.get_current_stage_beats()
    try:
        next_beats = simulated_state.get_next_stage_beats()
    except Exception:
        next_beats = []
    lines = ["Current stage beats:"]
    if current_beats:
        lines.extend(f"- {b.id}: {b.name} [{b.status}]" for b in current_beats)
    else:
        lines.append("(none)")
    lines.append("Next stage beats:")
    if next_beats:
        lines.extend(f"- {b.id}: {b.name} [{b.status}]" for b in next_beats)
    else:
        lines.append("(none)")
    message = "\n".join(lines)
    return Command(update={
        logs_field_to_update: [get_log_item("list_current_and_next_stage_beats", args, True, True, message)],
        messages_field_to_update: [
            ToolMessage(get_observation(simulated_state.narrative_beats_count(), "list_current_and_next_stage_beats", True, message), tool_call_id=tool_call_id)
        ]
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
    get_narrative_beat_details,
    get_failure_condition_details,
    list_active_beats,
    list_pending_beats,
    list_current_and_next_stage_beats,
]
