"""Tool functions used by the relationship agent."""

from typing import Annotated, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from core_game.character.schemas import RelationshipType
from ..schemas.simulated_relationships import (
    SimulatedRelationshipsModel,
    GetRelationshipDetailsArgs,
    FinalizeSimulationArgs,
    CreateRelationshipTypeArgs,
    CreateUndirectedRelationshipArgs,
    CreateDirectedRelationshipArgs,
    ModifyRelationshipIntensityArgs,
)


class ToolGetRelationshipDetailsArgs(GetRelationshipDetailsArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolFinalizeSimulationArgs(FinalizeSimulationArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolCreateRelationshipTypeArgs(CreateRelationshipTypeArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolCreateUndirectedRelationshipArgs(CreateUndirectedRelationshipArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolCreateDirectedRelationshipArgs(CreateDirectedRelationshipArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolModifyRelationshipIntensityArgs(ModifyRelationshipIntensityArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


@tool(args_schema=ToolGetRelationshipDetailsArgs)
def get_relationship_details(
    source_character_id: str,
    target_character_id: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
) -> str:
    """(QUERY tool) Get all relationships from source to target character."""
    args_model = GetRelationshipDetailsArgs(
        source_character_id=source_character_id,
        target_character_id=target_character_id,
    )
    return simulated_relationships_state.get_relationship_details(args_model)


@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
) -> dict:
    """Finalize the simulation with a justification."""
    args_model = FinalizeSimulationArgs(justification=justification)
    return simulated_relationships_state.finalize_simulation(args_model)


@tool(args_schema=ToolCreateRelationshipTypeArgs)
def create_relationship_type(
    name: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
    explanation: Optional[str] = None,
) -> str:
    """(MODIFICATION tool) Create a new relationship type."""
    args_model = CreateRelationshipTypeArgs(name=name, explanation=explanation)
    if name in simulated_relationships_state.relationship_types:
        return simulated_relationships_state._log_and_summarize(
            "create_relationship_type",
            args_model,
            False,
            f"Relationship type '{name}' already exists.",
        )
    simulated_relationships_state.relationship_types[name] = RelationshipType(
        name=name, explanation=explanation
    )
    return simulated_relationships_state._log_and_summarize(
        "create_relationship_type",
        args_model,
        True,
        f"Relationship type '{name}' created.",
    )


@tool(args_schema=ToolCreateUndirectedRelationshipArgs)
def create_undirected_relationship(
    character_a_id: str,
    character_b_id: str,
    relationship_type: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
    intensity: Optional[int] = None,
) -> str:
    """(MODIFICATION tool) Create a bidirectional relationship between two characters."""
    args_model = CreateUndirectedRelationshipArgs(
        character_a_id=character_a_id,
        character_b_id=character_b_id,
        relationship_type=relationship_type,
        intensity=intensity,
    )
    result_a = create_directed_relationship.func(
        source_character_id=character_a_id,
        target_character_id=character_b_id,
        relationship_type=relationship_type,
        simulated_relationships_state=simulated_relationships_state,
        intensity=intensity,
    )
    result_b = create_directed_relationship.func(
        source_character_id=character_b_id,
        target_character_id=character_a_id,
        relationship_type=relationship_type,
        simulated_relationships_state=simulated_relationships_state,
        intensity=intensity,
    )
    success = "already exists" not in result_a and "already exists" not in result_b
    message = (
        f"Undirected relationship '{relationship_type}' created between {character_a_id} and {character_b_id}."
        if success
        else "One or both directions already existed."
    )
    return simulated_relationships_state._log_and_summarize(
        "create_undirected_relationship",
        args_model,
        success,
        message,
    )


@tool(args_schema=ToolCreateDirectedRelationshipArgs)
def create_directed_relationship(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
    intensity: Optional[int] = None,
) -> str:
    """(MODIFICATION tool) Create a one-way relationship if it doesn't exist."""
    args_model = CreateDirectedRelationshipArgs(
        source_character_id=source_character_id,
        target_character_id=target_character_id,
        relationship_type=relationship_type,
        intensity=intensity,
    )
    existing = (
        simulated_relationships_state.relationships_matrix
        .get(source_character_id, {})
        .get(target_character_id, {})
        .get(relationship_type)
    )
    if existing is not None:
        return simulated_relationships_state._log_and_summarize(
            "create_directed_relationship",
            args_model,
            False,
            "Relationship already exists.",
        )

    r_type = simulated_relationships_state.relationship_types.get(relationship_type)
    if r_type is None:
        return simulated_relationships_state._log_and_summarize(
            "create_directed_relationship",
            args_model,
            False,
            f"Relationship type '{relationship_type}' not found.",
        )
    rel = CharacterRelationship(type=r_type, intensity=intensity)
    simulated_relationships_state.relationships_matrix.setdefault(source_character_id, {}).setdefault(
        target_character_id, {}
    )[relationship_type] = rel
    return simulated_relationships_state._log_and_summarize(
        "create_directed_relationship",
        args_model,
        True,
        f"Directed relationship '{relationship_type}' set from {source_character_id} to {target_character_id}.",
    )


@tool(args_schema=ToolModifyRelationshipIntensityArgs)
def modify_relationship_intensity(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    new_intensity: int,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
) -> str:
    """(MODIFICATION tool) Change the intensity of an existing relationship."""
    args_model = ModifyRelationshipIntensityArgs(
        source_character_id=source_character_id,
        target_character_id=target_character_id,
        relationship_type=relationship_type,
        new_intensity=new_intensity,
    )
    rel = (
        simulated_relationships_state.relationships_matrix
        .get(source_character_id, {})
        .get(target_character_id, {})
        .get(relationship_type)
    )
    if rel is None:
        return simulated_relationships_state._log_and_summarize(
            "modify_relationship_intensity",
            args_model,
            False,
            "Relationship not found.",
        )
    if rel.intensity is None:
        return simulated_relationships_state._log_and_summarize(
            "modify_relationship_intensity",
            args_model,
            False,
            "Relationship has no intensity to modify.",
        )
    rel.intensity = new_intensity
    return simulated_relationships_state._log_and_summarize(
        "modify_relationship_intensity",
        args_model,
        True,
        f"Intensity updated to {new_intensity}.",
    )


EXECUTORTOOLS = [
    create_relationship_type,
    create_undirected_relationship,
    create_directed_relationship,
    modify_relationship_intensity,
    get_relationship_details,
    finalize_simulation,
]
