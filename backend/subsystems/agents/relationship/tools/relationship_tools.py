"""Tool functions used by the relationship agent."""

from typing import Annotated, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from ..schemas.simulated_relationships import (
    SimulatedRelationshipsModel,
    SetRelationshipArgs,
    GetRelationshipDetailsArgs,
    FinalizeSimulationArgs,
)


class ToolSetRelationshipArgs(SetRelationshipArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolGetRelationshipDetailsArgs(GetRelationshipDetailsArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


class ToolFinalizeSimulationArgs(FinalizeSimulationArgs):
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")]


@tool(args_schema=ToolSetRelationshipArgs)
def set_relationship(
    source_character_id: str,
    target_character_id: str,
    relationship_type: str,
    simulated_relationships_state: Annotated[SimulatedRelationshipsModel, InjectedState("working_simulated_relationships")],
    intensity: Optional[int] = None,
) -> str:
    """(MODIFICATION tool) Set or update a relationship between two characters."""
    args_model = SetRelationshipArgs(
        source_character_id=source_character_id,
        target_character_id=target_character_id,
        relationship_type=relationship_type,
        intensity=intensity,
    )
    return simulated_relationships_state.set_relationship(args_model)


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


EXECUTORTOOLS = [
    set_relationship,
    get_relationship_details,
    finalize_simulation,
]
