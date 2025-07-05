from typing import Annotated, Optional, List, Literal, cast
import json
from pydantic import Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from .helpers import get_observation

# Assuming your schemas and activation_conditions are defined elsewhere
from core_game.game_event.schemas import (
    GameEventModel,
    NPCConversationEventModel,
    PlayerNPCConversationEventModel,
    NarratorInterventionEventModel,
    CutsceneEventModel
)
from core_game.game_event.activation_conditions.schemas import ActivationConditionModel
from core_game.game_event.activation_conditions.constants import *
from core_game.game_event.constants import EVENT_STATUS_LITERAL

# ---------------------------------------------------
# 1. SCHEMAS FOR TOOL ARGUMENTS
# ---------------------------------------------------

# --- Schemas for "all-in-one" convenience tools ---

class ToolCreateNPCConversationEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, human-readable name for this event. Example: 'Guards complain about salary'.")
    description: str = Field(..., description="The creative brief for the scene, guiding a future AI in writing the dialogue. For best results, provide context on the conversation's Topic, Goal, Tone, and others. (Max. 150-200 words)")
    npc_ids: List[str] = Field(..., description="List of IDs for the NPCs in the conversation. Must contain at least one ID. A single ID creates a monologue. Player CANNOT be in the list")
    activation_conditions: List[ActivationConditionsNPCConversation] = Field(..., description="The set of conditions that will trigger this event. The event will start once any of these conditions are met.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of a Narrative Beat to link this event to a specific part of the story.")

class ToolCreatePlayerNPCConversationEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, human-readable name for this event. Example: 'Elara asks player (Julius) about the key'.")
    description: str = Field(..., description="The creative brief for this interactive scene. This text guides a future AI in writing the dialogue. For a compelling interaction, consider including the scene's setup, the player's core objective or decision (e.g., 'The player must choose between joining three factions'), and the overall narrative goal. (Max. 150-200 words)")
    npc_ids: List[str] = Field(..., description="List of IDs for the NPCs participating in the conversation. Must contain at least one NPC. Player CANNOT be in the list, it is included automatically")
    activation_conditions: List[ActivationConditionsPlayerConversation] = Field(..., description="The set of conditions that will trigger this event. The event will start once any of these conditions are met.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of a Narrative Beat to link this event to a specific part of the story.")

class ToolCreateCutsceneEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, human-readable name for this cutscene. Example: 'The Castle Gates Explode'.")
    description: str = Field(..., description="The creative brief for the cutscene. This is a high-level script that guides a future AI in generating the final visuals and texts for the cutscene. Describe the sequence of key moments, outlining the core action, setting, topic, and any important dialogue or narration, including who is speaking (e.g., Narrator, a specific character ID, or 'Player'). (Max. 150-200 words)")
    involved_character_ids: Optional[List[str]] = Field(None, description="Optional: A list of character IDs who are present or relevant in the cutscene. This provides context for generating visuals. Player character id can be here too")
    involved_scenario_ids: Optional[List[str]] = Field(None, description="Optional: A list of scenario IDs for scenarios relevant in the cutscene. This provides context for the setting's visuals.")
    activation_conditions: List[ActivationConditionsCutscene] = Field(..., description="The set of conditions that will trigger this event. The event will start once any of these conditions are met.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of a Narrative Beat to link this event to a specific part of the story.")


class ToolCreateNarratorInterventionEventArgs(InjectedToolContext):
    title: str = Field(..., description="A short, human-readable name for the narrator intervention. Example: 'It starts raining ashes'.")
    description: str = Field(..., description="The creative brief for the intervention. This text will be used by a future AI to write the narrator's exact lines. Describe the observation, topic, information, or internal thought the player should experience.")
    activation_conditions: List[ActivationConditionsNarrator] = Field(..., description="The set of conditions that will trigger this event. The event will start once any of these conditions are met.")
    source_beat_id: Optional[str] = Field(None, description="Optional: The ID of a Narrative Beat to link this event to a specific part of the story.")

# --- Schemas for other tools ---

class ToolLinkActivationConditionsToEventArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to which the new activation conditions will be added.")
    activation_conditions: List[ActivationConditionsUnion] = Field(..., description="The set of conditions that will be added to trigger this event.")

class ToolListEventsArgs(InjectedToolContext):
    status_filter: Optional[EVENT_STATUS_LITERAL] = Field(None, description="Optional: Filter the list to show events only with this status.")

class ToolGetEventDetailsArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to inspect.")

class ToolDeleteEventArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to delete.")

class ToolUpdateEventDescriptionArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to update.")
    new_description: str = Field(..., description="The new director's brief for the event.")

class ToolUpdateEventTitleArgs(InjectedToolContext):
    event_id: str = Field(..., description="The ID of the event to update.")
    new_title: str = Field(..., description="The new title for the event.")

class ToolUnlinkActivationConditionArgs(InjectedToolContext):
    event_id: str = Field(..., description="ID of the event from which the condition will be removed.")
    condition_id: str = Field(..., description="ID of the activation condition to remove.")

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

@tool(args_schema=ToolCreateNPCConversationEventArgs)
def create_npc_conversation_event(
    title: str, description: str, npc_ids: List[str], activation_conditions: List[ActivationConditionsNPCConversation], source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Creates and adds a self-contained non interactive conversation event between NPCs.

    Use Case: This tool is for creating non-interactive scenes that the player
    overhears. The player CANNOT participate. It requires at least one NPC; if only one
    is provided, the event will be a monologue spoken by that character. Its applications
    are broad, including uses like ambient world-building, storytelling through
    background chatter, or scripted scenes. Feel free to use it for any creative
    purpose that fits a non-interactive conversation. The created event is made
    'AVAILABLE' immediately.
    """
    args = extract_tool_args(locals())
    
    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        conditions_for_orchestrator = cast(List[ActivationConditionModel], activation_conditions)

        created_event = simulated_state.create_available_npc_conversation(
            title=title,
            description=description,
            npc_ids=npc_ids,
            activation_conditions=conditions_for_orchestrator,
            source_beat_id=source_beat_id
        )
        
        success = True
        message = f"NPC Conversation event '{created_event.title}' (ID: {created_event.id}) was created successfully with status AVAILABLE."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_npc_conversation_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_npc_conversation_event", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreatePlayerNPCConversationEventArgs)
def create_player_npc_conversation_event(
    title: str,
    description: str,
    npc_ids: List[str],
    activation_conditions: List[ActivationConditionsPlayerConversation],
    source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Creates and adds an INTERACTIVE conversation involving the Player and NPCs.

    Use Case: This is the core tool for driving the story forward through player agency. 
    Its applications are broad, including creating scenes where the player's choices can directly influence relationships, unlock new paths, or permanently alter the narrative. 
    This event type is fundamental for creating meaningful consequences based on player decisions.
    The created event becomes 'AVAILABLE' immediately.
    """
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        conditions_for_orchestrator = cast(List[ActivationConditionModel], activation_conditions)
        created_event = simulated_state.create_available_player_npc_conversation(
            title=title,
            description=description,
            npc_ids=npc_ids,
            activation_conditions=conditions_for_orchestrator,
            source_beat_id=source_beat_id
        )
        
        success = True
        message = f"Player-NPC Conversation event '{created_event.title}' (ID: {created_event.id}) created successfully with status AVAILABLE."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_player_npc_conversation_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_player_npc_conversation_event", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateCutsceneEventArgs)
def create_cutscene_event(
    title: str, description: str, activation_conditions: List[ActivationConditionsCutscene], source_beat_id: Optional[str],
    involved_character_ids: Optional[List[str]],
    involved_scenario_ids: Optional[List[str]],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Creates and adds an a non-interactive, cinematic cutscene event.

    Use Case: This tool is for creating scripted sequences where the player loses
    control and watches events unfold. Its applications
    are broad, including uses like major plot points,
    character introductions, flashbacks, imaginations, environmental events, or anything that would be great to be accompanied by specific visuals. The created event is made
    'AVAILABLE' immediately.
    """
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        conditions_for_orchestrator = cast(List[ActivationConditionModel], activation_conditions)
        created_event = simulated_state.create_available_cutscene(
            title=title,
            description=description,
            activation_conditions=conditions_for_orchestrator,
            source_beat_id=source_beat_id,
            involved_character_ids=involved_character_ids,
            involved_scenario_ids=involved_scenario_ids
        )
        
        success = True
        message = f"Cutscene event '{created_event.title}' (ID: {created_event.id}) was created successfully with status AVAILABLE."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_cutscene_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_cutscene_event", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolCreateNarratorInterventionEventArgs)
def create_narrator_intervention_event(
    title: str,
    description: str,
    activation_conditions: List[ActivationConditionsNarrator],
    source_beat_id: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Constructs and activates a narrator intervention event.

    Use Case: This tool is for making the narrator speak directly to the player,
    describe something in the environment, or convey the player's internal thoughts.
    Its applications are broad, including uses like providing clues, setting a scene, or revealing lore. The created
    event is made 'AVAILABLE' immediately.
    """
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        conditions_for_orchestrator = cast(List[ActivationConditionModel], activation_conditions)
        created_event = simulated_state.create_available_narrator_intervention(
            title=title,
            description=description,
            activation_conditions=conditions_for_orchestrator,
            source_beat_id=source_beat_id
        )
        
        success = True
        message = f"Narrator Intervention event '{created_event.title}' (ID: {created_event.id}) was created successfully with status AVAILABLE."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("create_narrator_intervention_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("create_narrator_intervention_event", success, message), tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolLinkActivationConditionsToEventArgs)
def link_activation_conditions_to_event(
    event_id: str,
    activation_conditions: List[ActivationConditionsUnion],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    Adds one or more new activation conditions to an existing event in  'AVAILABLE' Status.
    """
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        conditions_for_orchestrator = cast(List[ActivationConditionModel], activation_conditions)
        simulated_state.link_conditions_to_event(
            event_id=event_id,
            conditions=conditions_for_orchestrator
        )
        
        success = True
        message = f"Successfully linked new activation conditions to event '{event_id}'."

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("link_activation_conditions_to_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("link_activation_conditions_to_event", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolListEventsArgs)
def list_events(
    status_filter: Optional[EVENT_STATUS_LITERAL],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """
    (QUERY) Lists existing game events. If a status is provided, it returns a
    filtered list. Otherwise, it provides a structured overview of all events,
    grouped by their narrative beat and then by status. For each event it shows title, id, status, source beat id and type
    """
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    
    try:
        if status_filter:
            event_list = simulated_state.read_only_events.list_events(status=status_filter)
            
            if not event_list:
                message = f"No events found with status '{status_filter}'."
            else:
                # Manual formatting for a cleaner, more readable output for the LLM
                message_parts = [f"Found {len(event_list)} events with status '{status_filter}':"]
                for event in event_list:
                    source_beat_id = event.source_beat_id
                    beat_info_str = "BEATLESS"
                    if source_beat_id:
                        beat = simulated_state.read_only_narrative.get_beat(source_beat_id)
                        beat_name = f" (\"{beat.name}\")" if beat and hasattr(beat, 'name') else " (Not Found)"
                        beat_info_str = f"{source_beat_id} {beat_name}"

                    message_parts.append(f"  - ID: {event.id}, Title: \"{event.title}\", Type: {event.get_model().type}, Status: {event.status}, Source Beat: [{beat_info_str}]")
                message = "\n".join(message_parts)
        else:
            # --- Logic for when NO filter is provided: Group by beat and then by status ---
            grouped_events = simulated_state.read_only_events.get_all_events_grouped()
            
            if not grouped_events:
                message = "No events found in the game."
            else:
                message_parts = ["Overview of all game events:"]
                sorted_beat_ids = sorted(grouped_events.keys(), key=lambda k: (k == "BEATLESS", k))

                for beat_id in sorted_beat_ids:
                    beat_header = beat_id
                    if beat_id != "BEATLESS":
                        beat = simulated_state.read_only_narrative.get_beat(beat_id)
                        if beat and hasattr(beat, 'name'):
                            beat_header = f"{beat_id} (\"{beat.name}\")"

                    events_by_status = grouped_events[beat_id]
                    message_parts.append(f"\n\n--- NARRATIVE BEAT: {beat_header} ---")
                    for status in sorted(events_by_status.keys()):
                        events = events_by_status[status]
                        message_parts.append(f"\n  - STATUS: {status.upper()}")
                        for event in events:
                            message_parts.append(f"    - ID: {event.id}, Title: \"{event.title}\", Type: {event.get_model().type}")
                message = "\n".join(message_parts)
        
        success = True

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("list_events", args, True, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("list_events", success, message), tool_call_id=tool_call_id)],
    })

@tool(args_schema=ToolGetEventDetailsArgs)
def get_event_details(
    event_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """(QUERY) Retrieves all details for a single, specific game event by its ID. With this tool you will obtain the description and activation conditions of an event (between others)"""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    
    try:
        event = simulated_state.read_only_events.find_event(event_id)
        
        if not event:
            raise KeyError(f"Event with ID '{event_id}' not found.")
        
        details = event.get_model().model_dump_json(indent=2)
        message = f"Details for event '{event_id}':\n{details}"
        success = True

    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("get_event_details", args, True, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("get_event_details", success, message), tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolDeleteEventArgs)
def delete_event(
    event_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Permanently removes an event from the game state."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    try:
        event = simulated_state.delete_event(event_id)
        success = True
        message = f"Event '{event_id}' deleted successfully."
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("delete_event", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("delete_event", success, message), tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolUpdateEventDescriptionArgs)
def update_event_description(
    event_id: str,
    new_description: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Updates the director's brief of an existing event."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    try:
        simulated_state.update_event_description(event_id, new_description)
        success = True
        message = f"Description for event '{event_id}' updated."
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("update_event_description", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("update_event_description", success, message), tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolUpdateEventTitleArgs)
def update_event_title(
    event_id: str,
    new_title: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Updates the title of an existing event."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    try:
        simulated_state.update_event_title(event_id, new_title)
        success = True
        message = f"Title for event '{event_id}' updated."
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("update_event_title", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("update_event_title", success, message), tool_call_id=tool_call_id)],
    })


@tool(args_schema=ToolUnlinkActivationConditionArgs)
def unlink_activation_condition(
    event_id: str,
    condition_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Removes a specific activation condition from an event."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    try:
        simulated_state.unlink_condition_from_event(event_id, condition_id)
        success = True
        message = f"Condition '{condition_id}' removed from event '{event_id}'."
    except Exception as e:
        success = False
        message = str(e)

    return Command(update={
        logs_field_to_update: [get_log_item("unlink_activation_condition", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation("unlink_activation_condition", success, message), tool_call_id=tool_call_id)],
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
    create_npc_conversation_event,
    create_player_npc_conversation_event,
    create_cutscene_event,
    create_narrator_intervention_event,
    link_activation_conditions_to_event,
    delete_event,
    update_event_description,
    update_event_title,
    unlink_activation_condition,

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
