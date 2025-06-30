"""Tool functions used by the relationship handler agent."""

from typing import Optional, Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage


from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args
from .helpers import get_observation
from simulated.singleton import SimulatedGameStateSingleton

# --- Tool schemas ---
class ToolCreateRelationshipTypeArgs(InjectedToolContext):
    name: str = Field(..., description="Name of the relationship type")
    explanation: Optional[str] = Field(default=None, description="Explanation of the relationship type")

class ToolCreateDirectedRelationshipArgs(InjectedToolContext):
    source_character_id: str = Field(
        ..., description="ID of the character initiating the relationship"
    )
    target_character_id: str = Field(
        ..., description="ID of the character receiving the relationship"
    )
    relationship_type: str = Field(
        ..., description="Name of the relationship type to create"
    )
    intensity: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Optional intensity value from 0 to 10",
    )

class ToolCreateUndirectedRelationshipArgs(InjectedToolContext):
    character_a_id: str = Field(
        ..., description="ID of the first character in the relationship"
    )
    character_b_id: str = Field(
        ..., description="ID of the second character in the relationship"
    )
    relationship_type: str = Field(
        ..., description="Name of the relationship type to create"
    )
    intensity: Optional[int] = Field(
        default=None,
        ge=0,
        le=10,
        description="Optional intensity value from 0 to 10",
    )

class ToolModifyRelationshipIntensityArgs(InjectedToolContext):
    source_character_id: str = Field(
        ..., description="ID of the character initiating the relationship"
    )
    target_character_id: str = Field(
        ..., description="ID of the relationship target"
    )
    relationship_type: str = Field(
        ..., description="Relationship type whose intensity will be modified"
    )
    new_intensity: int = Field(
        ..., ge=0, le=10, description="New intensity value from 0 to 10"
    )

class ToolGetRelationshipDetailsArgs(InjectedToolContext):
    source_character_id: str = Field(
        ..., description="ID of the character initiating the relationship"
    )
    target_character_id: str = Field(
        ..., description="ID of the character receiving the relationship"
    )

class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str = Field(
        ..., description="Explanation of why the relationships meet the objective"
    )

# --- Tool implementations ---
@tool(args_schema=ToolCreateRelationshipTypeArgs)
def create_relationship_type(
    name: str,
    explanation: Optional[str],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create a new relationship type in the simulated game state."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.create_relationship_type(name=name, explanation=explanation)
        message = f"Relationship type '{name}' created."
    except ValueError as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("create_relationship_type", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "create_relationship_type", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolCreateDirectedRelationshipArgs)
def create_directed_relationship(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    intensity: Optional[int],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create a directed relationship from one character to another."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.create_directed_relationship(
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            relationship_type=relationship_type,
            intensity=intensity,
        )
        message = f"Relationship '{relationship_type}' created from {source_character_id} to {target_character_id}."
    except ValueError as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("create_directed_relationship", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "create_directed_relationship", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolCreateUndirectedRelationshipArgs)
def create_undirected_relationship(
    character_a_id: str,
    character_b_id: str,
    relationship_type: str,
    intensity: Optional[int],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create an undirected relationship between two characters."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.create_undirected_relationship(
            character_a_id=character_a_id,
            character_b_id=character_b_id,
            relationship_type=relationship_type,
            intensity=intensity,
        )
        message = f"Undirected relationship '{relationship_type}' created between {character_a_id} and {character_b_id}."
    except ValueError as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("create_undirected_relationship", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "create_undirected_relationship", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolModifyRelationshipIntensityArgs)
def modify_relationship_intensity(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    new_intensity: int,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Modify the intensity of an existing relationship."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.modify_relationship_intensity(
            source_character_id=source_character_id,
            target_character_id=target_character_id,
            relationship_type=relationship_type,
            new_intensity=new_intensity,
        )
        message = f"Intensity updated to {new_intensity}."
    except (KeyError, ValueError) as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("modify_relationship_intensity", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "modify_relationship_intensity", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolGetRelationshipDetailsArgs)
def get_relationship_details(
    source_character_id: str,
    target_character_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Retrieve relationship details from one character to another."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    rels = simulated_state.get_relationship_details(source_character_id, target_character_id)
    if not rels:
        message = "No relationship found."
        success = False
    else:
        lines = [f"{name}: intensity {rel.intensity}" for name, rel in rels.items()]
        message = " | ".join(lines)
        success = True
    return Command(update={
        logs_field_to_update: [get_log_item("get_relationship_details", args, True, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "get_relationship_details", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Mark the relationships simulation as completed."""
    simulated_state = SimulatedGameStateSingleton.get_instance()
    args = extract_tool_args(locals())
    message = "Simulation finalized."
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.get_relationship_count(), "finalize_simulation", True, message), tool_call_id=tool_call_id)],
        "relationships_task_finalized_by_agent": True,
        "relationships_task_finalized_justification": justification,
    })

EXECUTORTOOLS = [
    create_relationship_type,
    create_directed_relationship,
    create_undirected_relationship,
    modify_relationship_intensity,
    get_relationship_details,
    finalize_simulation,
]

VALIDATIONTOOLS = [
    get_relationship_details,
]

QUERYTOOLS = [
    get_relationship_details,
]
