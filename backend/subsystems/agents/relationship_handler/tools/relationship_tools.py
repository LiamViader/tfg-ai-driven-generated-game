
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
        ...,
        description="Name of an existing relationship type. Use 'create_relationship_type' first if needed"
    )
    intensity: int = Field(
        ...,
        ge=0,
        le=10,
        description="Intensity value from 0 to 10",
    )

class ToolCreateUndirectedRelationshipArgs(InjectedToolContext):
    character_a_id: str = Field(
        ..., description="ID of the first character in the relationship"
    )
    character_b_id: str = Field(
        ..., description="ID of the second character in the relationship"
    )
    relationship_type: str = Field(
        ...,
        description="Name of an existing relationship type. Use 'create_relationship_type' first if needed"
    )
    intensity: int = Field(
        ...,
        ge=0,
        le=10,
        description="Intensity value from 0 to 10",
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


class ToolValidateSimulatedRelationshipsArgs(InjectedToolContext):
    does_relationships_meet_criteria: bool = Field(
        ..., description="Assessment flag: True if the relationships meet the objective, False otherwise"
    )
    assessment_reasoning: str = Field(
        ..., description="Reasoning behind the validation outcome"
    )
    suggested_improvements: Optional[str] = Field(
        default=None,
        description="Suggestions on how to improve if validation failed",
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
    """Create a new relationship type if it doesn't already exist."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.relationships.create_relationship_type(name=name, explanation=explanation)
        message = f"Relationship type '{name}' created."
    except ValueError as e:
        success = False
        message = str(e)
    return Command(update={
        logs_field_to_update: [get_log_item("create_relationship_type", args, False, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "create_relationship_type", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolCreateDirectedRelationshipArgs)
def create_directed_relationship(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    intensity: int,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create a directed relationship between two characters. The relationship type must already exist."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.relationships.create_directed_relationship(
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
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "create_directed_relationship", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolCreateUndirectedRelationshipArgs)
def create_undirected_relationship(
    character_a_id: str,
    character_b_id: str,
    relationship_type: str,
    intensity: int,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Create an undirected relationship between two characters. The relationship type must already exist."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    success = True
    try:
        simulated_state.relationships.create_undirected_relationship(
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
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "create_undirected_relationship", success, message), tool_call_id=tool_call_id)]
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
        simulated_state.relationships.modify_relationship_intensity(
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
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "modify_relationship_intensity", success, message), tool_call_id=tool_call_id)]
    })

@tool(args_schema=ToolGetRelationshipDetailsArgs)
def get_relationship_details(
    source_character_id: str,
    target_character_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Retrieve details of relationships from one character to another."""
    args = extract_tool_args(locals())
    simulated_state = SimulatedGameStateSingleton.get_instance()
    rels = simulated_state.read_only_relationships.get_relationship_details(source_character_id, target_character_id)
    if not rels:
        message = "No relationship found."
        success = False
    else:
        lines = [f"{name}: intensity {rel.intensity}" for name, rel in rels.items()]
        rel_text = " | ".join(lines)
        message = f"(from {source_character_id} to {target_character_id}) {rel_text}"
        success = True
    return Command(update={
        logs_field_to_update: [get_log_item("get_relationship_details", args, True, success, message)],
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "get_relationship_details", success, message), tool_call_id=tool_call_id)]
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
        messages_field_to_update: [ToolMessage(get_observation(simulated_state.read_only_relationships.relationship_count(), "finalize_simulation", True, message), tool_call_id=tool_call_id)],
        "relationships_task_finalized_by_agent": True,
        "relationships_task_finalized_justification": justification,
    })


@tool(args_schema=ToolValidateSimulatedRelationshipsArgs)
def validate_simulated_relationships(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    does_relationships_meet_criteria: bool,
    assessment_reasoning: str,
    suggested_improvements: Optional[str] = None,
) -> Command:
    """Validates the simulated relationships state. Call when you are sure the objective is met or not."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    if not suggested_improvements:
        suggested_improvements = ""

    if does_relationships_meet_criteria:
        message = f"Simulated relationships meet all criteria. Reason: {assessment_reasoning}"
    else:
        message = (
            f"Simulated relationships don't meet all criteria. Reason: {assessment_reasoning}. "
            f"Suggestions: {suggested_improvements}"
        )

    return Command(update={
        logs_field_to_update: [get_log_item("validate_simulated_relationships", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.read_only_relationships.relationship_count(), "validate_simulated_relationships", True, message),
                tool_call_id=tool_call_id,
            )
        ],
        "relationships_agent_validated": True,
        "relationships_agent_validation_conclusion_flag": does_relationships_meet_criteria,
        "relationships_agent_validation_assessment_reasoning": assessment_reasoning,
        "relationships_agent_validation_suggested_improvements": suggested_improvements,
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
    validate_simulated_relationships,
]

QUERYTOOLS = [
    get_relationship_details,
]
