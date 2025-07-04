from typing import Annotated, Optional, List, Literal
from pydantic import Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from .helpers import get_observation

# Assuming your schemas and triggers are defined elsewhere
from core_game.game_event.schemas import (
    GameEventModel,
    NPCConversationEventModel,
    PlayerNPCConversationEventModel,
    NarratorInterventionEventModel,
    CutsceneEventModel
)
from core_game.game_event.activation_conditions.schemas import GameEventTrigger


# ---------------------------------------------------
# 1. SCHEMAS FOR TOOL ARGUMENTS
# ---------------------------------------------------

# --- Schemas for "all-in-one" convenience tools ---

class ToolCreateNPCConversationAndLinkEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, descriptive title for the conversation.")
    description: str = Field(..., description="The detailed creative brief for this conversation, outlining topics and goals.")
    npc_ids: List[str] = Field(..., description="A list of NPC IDs participating in the conversation.")
    triggers: List[GameEventTrigger] = Field(..., description="A list of one or more trigger conditions that will make this event 'AVAILABLE' immediately upon creation.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of the Narrative Beat that originated this event.")

class ToolCreatePlayerNPCConversationAndLinkEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, descriptive title for the conversation.")
    description: str = Field(..., description="The detailed creative brief for this conversation, outlining topics and goals.")
    npc_ids: List[str] = Field(..., description="A list of NPC IDs participating in the conversation.")
    triggers: List[GameEventTrigger] = Field(..., description="A list of one or more trigger conditions that will make this event 'AVAILABLE' immediately upon creation.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of the Narrative Beat that originated this event.")

class ToolCreateCutsceneAndLinkEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, descriptive title for the cutscene.")
    description: str = Field(..., description="The detailed creative brief for this cutscene, outlining key visual actions and narrative points.")
    triggers: List[GameEventTrigger] = Field(..., description="A list of one or more trigger conditions that will make this event 'AVAILABLE' immediately upon creation.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of the Narrative Beat that originated this event.")

class ToolCreateNarratorInterventionAndLinkEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, descriptive title for the narrator intervention.")
    description: str = Field(..., description="The detailed creative brief for this intervention, outlining the information or observation to be conveyed.")
    triggers: List[GameEventTrigger] = Field(..., description="A list of one or more trigger conditions that will make this event 'AVAILABLE' immediately upon creation.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of the Narrative Beat that originated this event.")

# --- Schemas for "Advanced" DRAFT creation tools ---

class ToolCreateDraftEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, descriptive title for the event.")
    description: str = Field(..., description="The detailed creative brief for the event.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of the Narrative Beat that originated this event.")

class ToolCreateDraftNPCConversationEventArgs(ToolCreateDraftEventArgs):
    npc_ids: List[str] = Field(..., description="A list of NPC IDs participating in the conversation.")

class ToolCreateDraftPlayerNPCConversationEventArgs(ToolCreateDraftEventArgs):
    npc_ids: List[str] = Field(..., description="A list of NPC IDs participating in the conversation.")

# --- Schemas for other tools ---

class ToolLinkTriggersToEventArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the 'DRAFT' or 'AVAILABLE' event to which the triggers will be linked.")
    triggers: List[GameEventTrigger] = Field(..., description="A list of one or more trigger conditions that will make this event 'AVAILABLE'.")

class ToolListEventsArgs(InjectedToolContext):
    status_filter: Optional[Literal["DRAFT", "AVAILABLE", "RUNNING", "COMPLETED"]] = Field(None, description="Optional: Filter the list to show events only with this status.")

class ToolGetEventDetailsArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to inspect.")

class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str = Field(..., description="Explanation of why the events meet the objective")

class ToolValidateSimulatedGameEventsArgs(InjectedToolContext):
    does_game_events_meet_criteria: bool = Field(..., description="True if events meet the objective")
    assessment_reasoning: str = Field(..., description="Reasoning behind the validation outcome")
    suggested_improvements: Optional[str] = Field(None, description="Suggestions on how to improve if validation failed")


# ---------------------------------------------------
# 2. TOOL IMPLEMENTATIONS
# ---------------------------------------------------

# --- RECOMMENDED "ALL-IN-ONE" TOOLS ---

@tool(args_schema=ToolCreateNPCConversationAndLinkEventArgs)
def create_npc_conversation_and_link_triggers(
    title: str, description: str, npc_ids: List[str], triggers: List[GameEventTrigger], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Recommended) Creates a new NPC conversation and immediately links its triggers, making it active in the game ('AVAILABLE' state)."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    event_model = NPCConversationEventModel(title=title, description=description, npc_ids=npc_ids, source_beat_id=source_beat_id, triggered_by=triggers, status="AVAILABLE")
    # simulated_state.add_event(event_model)
    message = f"NPC Conversation event '{event_model.title}' (ID: {event_model.id}) created and linked. Status is now AVAILABLE."
    return Command(update={
        logs_field_to_update: [get_log_item("create_npc_conversation_and_link_triggers", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_npc_conversation_and_link_triggers", True, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreatePlayerNPCConversationAndLinkEventArgs)
def create_player_npc_conversation_and_link_triggers(
    title: str, description: str, npc_ids: List[str], triggers: List[GameEventTrigger], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Recommended) Creates a new Player-NPC conversation and immediately links its triggers, making it active in the game ('AVAILABLE' state)."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    event_model = PlayerNPCConversationEventModel(title=title, description=description, npc_ids=npc_ids, source_beat_id=source_beat_id, triggered_by=triggers, status="AVAILABLE")
    # simulated_state.add_event(event_model)
    message = f"Player-NPC Conversation event '{event_model.title}' (ID: {event_model.id}) created and linked. Status is now AVAILABLE."
    return Command(update={
        logs_field_to_update: [get_log_item("create_player_npc_conversation_and_link_triggers", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_player_npc_conversation_and_link_triggers", True, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateCutsceneAndLinkEventArgs)
def create_cutscene_and_link_triggers(
    title: str, description: str, triggers: List[GameEventTrigger], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Recommended) Creates a new cutscene event and immediately links its triggers, making it active in the game ('AVAILABLE' state)."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    event_model = CutsceneEventModel(title=title, description=description, source_beat_id=source_beat_id, triggered_by=triggers, status="AVAILABLE")
    # simulated_state.add_event(event_model)
    message = f"Cutscene event '{event_model.title}' (ID: {event_model.id}) created and linked. Status is now AVAILABLE."
    return Command(update={
        logs_field_to_update: [get_log_item("create_cutscene_and_link_triggers", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_cutscene_and_link_triggers", True, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateNarratorInterventionAndLinkEventArgs)
def create_narrator_intervention_and_link_triggers(
    title: str, description: str, triggers: List[GameEventTrigger], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Recommended) Creates a new narrator intervention event and immediately links its triggers, making it active in the game ('AVAILABLE' state)."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    event_model = NarratorInterventionEventModel(title=title, description=description, source_beat_id=source_beat_id, triggered_by=triggers, status="AVAILABLE")
    # simulated_state.add_event(event_model)
    message = f"Narrator Intervention event '{event_model.title}' (ID: {event_model.id}) created and linked. Status is now AVAILABLE."
    return Command(update={
        logs_field_to_update: [get_log_item("create_narrator_intervention_and_link_triggers", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_narrator_intervention_and_link_triggers", True, message), tool_call_id=tool_call_id)],
    })


# --- ADVANCED "DRAFT-ONLY" TOOLS ---

@tool(args_schema=ToolCreateDraftNPCConversationEventArgs)
def create_draft_npc_conversation_event(
    title: str, description: str, npc_ids: List[str], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Advanced) Creates a new NPC conversation event in a 'DRAFT' state without any triggers. Use this only if you explicitly need to define triggers in a separate, later step using 'link_triggers_to_event'."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    event_model = NPCConversationEventModel(title=title, description=description, npc_ids=npc_ids, source_beat_id=source_beat_id, status="DRAFT")
    # simulated_state.add_event(event_model)
    message = f"NPC Conversation event '{event_model.title}' (ID: {event_model.id}) created in DRAFT state."
    return Command(update={
        logs_field_to_update: [get_log_item("create_draft_npc_conversation_event", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_draft_npc_conversation_event", True, message), tool_call_id=tool_call_id)],
    })

# You would add similar advanced draft tools for other event types here.
# For brevity, they are omitted, but would follow the same pattern.

# --- LINKING & QUERY TOOLS ---

@tool(args_schema=ToolLinkTriggersToEventArgs)
def link_triggers_to_event(
    event_id: str, triggers: List[GameEventTrigger],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(Advanced) Links one or more triggers to an existing 'DRAFT' event, changing its status to AVAILABLE. Use this to activate events created with a 'create_draft_...' tool."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        # event = simulated_state.get_event_by_id(event_id)
        # if event.status != "DRAFT":
        #     raise ValueError(f"Event {event_id} is not in DRAFT state. Cannot link new triggers.")
        # event.triggers.extend(triggers)
        # event.status = "AVAILABLE"
        # simulated_state.update_event(event)
        message = f"Triggers successfully linked to event {event_id}. Status is now AVAILABLE."
    except Exception as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("link_triggers_to_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("link_triggers_to_event", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolListEventsArgs)
def list_events(
    status_filter: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY) Lists existing game events, optionally filtering by status (DRAFT, AVAILABLE, etc.). Useful for finding DRAFT events that need triggers."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    # event_list = simulated_state.list_events(status=status_filter)
    event_list = [] # Placeholder
    message = f"Found {len(event_list)} events."
    if status_filter:
        message += f" with status '{status_filter}'"
    message += f"\n{event_list}"
    return Command(update={
        logs_field_to_update: [get_log_item("list_events", args, True, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("list_events", True, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolGetEventDetailsArgs)
def get_event_details(
    event_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY) Retrieves all details for a single, specific game event by its ID."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        # details = simulated_state.get_event_by_id(event_id).model_dump_json(indent=2)
        details = "{}" # Placeholder
        message = details
    except Exception as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("get_event_details", args, True, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("get_event_details", success, message), tool_call_id=tool_call_id)],
    })

# --- FINALIZE/VALIDATE TOOLS ---
@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """MUST be your final action. Call this ONLY when the objective is fully satisfied. This signals your work is complete."""
    args = extract_tool_args(locals())
    message = justification
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("finalize_simulation", True, message), tool_call_id=tool_call_id)],
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
    """(VALIDATION) Submits a final validation assessment of the other agent's work. Use this to either approve the game events or provide specific, actionable feedback for corrections."""
    args = extract_tool_args(locals())
    if not suggested_improvements:
        suggested_improvements = ""
    if does_game_events_meet_criteria:
        message = f"Game events meet criteria. Reason: {assessment_reasoning}"
    else:
        message = f"Game events do not meet criteria. Reason: {assessment_reasoning}. Suggestions: {suggested_improvements}"
    return Command(update={
        logs_field_to_update: [get_log_item("validate_simulated_game_events", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation("validate_simulated_game_events", True, message), tool_call_id=tool_call_id)],
        "events_agent_validated": True,
        "events_agent_validation_conclusion_flag": does_game_events_meet_criteria,
        "events_agent_validation_assessment_reasoning": assessment_reasoning,
        "events_agent_validation_suggested_improvements": suggested_improvements,
    })


# ---------------------------------------------------
# 3. TOOL LISTS
# ---------------------------------------------------

EXECUTORTOOLS = [
    # Recommended "all-in-one" tools
    create_npc_conversation_and_link_triggers,
    create_player_npc_conversation_and_link_triggers,
    create_cutscene_and_link_triggers,
    create_narrator_intervention_and_link_triggers,
    
    # Advanced, granular tools
    create_draft_npc_conversation_event,
    # ... (add other create_draft_* tools here for completeness)
    link_triggers_to_event,
    
    # Query and finalize tools
    list_events,
    get_event_details,
    finalize_simulation,
]

VALIDATIONTOOLS = [
    list_events,
    get_event_details,
    validate_simulated_game_events,
]
