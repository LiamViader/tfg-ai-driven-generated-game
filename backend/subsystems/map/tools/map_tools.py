from typing import Dict, List, Any, Optional, Literal, Set, Tuple, Annotated
from pydantic import BaseModel, Field as PydanticField
from langchain_core.tools import tool
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from core_game.map.schemas import Direction, OppositeDirections
from subsystems.map.schemas.simulated_map import *
from subsystems.map.service import MapService


# --- Tools Schemas -- (adding the injected simulated map)
class ToolCreateScenarioArgs(CreateScenarioArgs):
    map_service: Annotated[MapService, InjectedState("map_service")]

class ToolModifyScenarioArgs(ModifyScenarioArgs):
    map_service: Annotated[Optional[MapService], InjectedState("map_service")]

class ToolDeleteScenarioArgs(DeleteScenarioArgs):
    map_service: Annotated[MapService, InjectedState("map_service")]

class ToolCreateBidirectionalConnectionArgs(CreateBidirectionalConnectionArgs):
    map_service: Annotated[Optional[MapService], InjectedState("map_service")]

class ToolDeleteBidirectionalConnectionArgs(DeleteBidirectionalConnectionArgs):
    map_service: Annotated[MapService, InjectedState("map_service")]

class ToolModifyBidirectionalConnectionArgs(ModifyBidirectionalConnectionArgs):
    map_service: Annotated[Optional[MapService], InjectedState("map_service")]

class ToolGetScenarioDetailsArgs(GetScenarioDetailsArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolGetNeighborsAtDistanceArgs(GetNeighborsAtDistanceArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolListScenariosClusterSummaryArgs(ListScenariosClusterSummaryArgs):
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")]

class ToolFindScenariosArgs(FindScenariosArgs):
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")]

class ToolGetBidirectionalConnectionDetailsArgs(GetBidirectionalConnectionDetailsArgs): 
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolGetAvailableExitsArgs(GetAvailableExitsArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolFinalizeSimulationArgs(FinalizeSimulationArgs):
    map_service: Annotated[MapService, InjectedState("map_service")]

class ToolValidateSimulatedMapArgs(ValidateSimulationMapArgs):
    map_service: Annotated[MapService, InjectedState("map_service")]

# --- Tools ---

@tool(args_schema=ToolCreateScenarioArgs)
def create_scenario(
    name: str, 
    narrative_context: str, 
    visual_description: str, 
    summary_description: str, 
    indoor_or_outdoor: Literal["indoor", "outdoor"],
    type: str,
    zone: str,
    map_service: Annotated[MapService, InjectedState("map_service")]
) -> str:
    """Creates a new scenario in the simulated map."""
    args_model = CreateScenarioArgs(
        name=name,
        summary_description=summary_description,
        visual_description=visual_description,
        narrative_context=narrative_context,
        indoor_or_outdoor=indoor_or_outdoor,
        type=type,
        zone=zone
    )
    return map_service.create_scenario(args_model)

@tool(args_schema=ToolModifyScenarioArgs)
def modify_scenario(
    scenario_id: str,
    new_name: Optional[str] = None,
    new_summary_description: Optional[str] = None,
    new_visual_description: Optional[str] = None,
    new_narrative_context: Optional[str] = None,
    new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = None,
    new_type: Optional[str] = None,
    new_zone: Optional[str] = None,
    map_service: Annotated[Optional[MapService], InjectedState("map_service")] = None
) -> str:
    """Modifies the specified scenario. Only the provided fields will be updated."""
    args_model = ModifyScenarioArgs(
        scenario_id=scenario_id,
        new_name=new_name,
        new_summary_description=new_summary_description,
        new_visual_description=new_visual_description,
        new_narrative_context=new_narrative_context,
        new_indoor_or_outdoor=new_indoor_or_outdoor,
        new_type=new_type,
        new_zone=new_zone
    )
    assert map_service is not None, "Injected state not received"
    return map_service.modify_scenario(args_model)

@tool(args_schema=ToolDeleteScenarioArgs)
def delete_scenario(
    scenario_id: str,
    map_service: Annotated[MapService, InjectedState("map_service")]
) -> str:
    """Deletes the specified scenario. An scenario should only be deleted if necessary to complete the task"""
    args_model = DeleteScenarioArgs(
        scenario_id=scenario_id,
    )
    return map_service.delete_scenario(args_model)

@tool(args_schema=ToolCreateBidirectionalConnectionArgs)
def create_bidirectional_connection(
    from_scenario_id: str, 
    direction_from_origin: Direction, 
    to_scenario_id: str, 
    connection_type: str, 
    travel_description: Optional[str] = None, 
    traversal_conditions: Optional[List[str]] = None,
    map_service: Annotated[Optional[MapService], InjectedState("map_service")] = None
) -> str:
    """Creates a new bidirectional connection between two existing scenarios in the simulation."""

    args_model = CreateBidirectionalConnectionArgs(
        from_scenario_id=from_scenario_id, 
        direction_from_origin=direction_from_origin,
        to_scenario_id=to_scenario_id, 
        connection_type=connection_type,
        travel_description=travel_description, 
        traversal_conditions=traversal_conditions or []
    )
    assert map_service is not None, "Injected state not received"
    return map_service.create_bidirectional_connection(args_model)


@tool(args_schema=ToolDeleteBidirectionalConnectionArgs)
def delete_bidirectional_connection(scenario_id_A: str, direction_from_A: Direction, map_service: Annotated[MapService, InjectedState("map_service")]) -> str:
    """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""
    args_model = DeleteBidirectionalConnectionArgs(scenario_id_A=scenario_id_A, direction_from_A=direction_from_A)
    return map_service.delete_bidirectional_connection(args_model)

@tool(args_schema=ToolModifyBidirectionalConnectionArgs)
def modify_bidirectional_connection(
    from_scenario_id: str, 
    direction_from_origin: Direction,
    new_connection_type: Optional[str] = None,
    new_travel_description: Optional[str] = None,
    new_traversal_conditions: Optional[List[str]] = None,
    map_service: Annotated[Optional[MapService], InjectedState("map_service")] = None
) -> str:
    """Modifies attributes of an existing bidirectional connection. Only provided attributes are changed."""
    
    args_model = ModifyBidirectionalConnectionArgs(
        from_scenario_id=from_scenario_id, 
        direction_from_origin=direction_from_origin,
        new_connection_type=new_connection_type, 
        new_travel_description=new_travel_description,
        new_traversal_conditions=new_traversal_conditions
    )
    assert map_service is not None, "Injected state not received"
    return map_service.modify_bidirectional_connection(args_model)

@tool(args_schema=ToolGetScenarioDetailsArgs)
def get_scenario_details(scenario_id: str, simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """(QUERY tool) Retrieves and returns all details for a specific scenario in the simulated map."""
    args_model = GetScenarioDetailsArgs(scenario_id=scenario_id)
    return simulated_map_state.get_scenario_details(args_model=args_model)

@tool(args_schema=ToolGetNeighborsAtDistanceArgs)
def get_neighbors_at_distance(start_scenario_id: str, max_distance: int,simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """(QUERY tool) Retrieves scenarios within N hops from a starting scenario, including connection details. Use this to understand spatial composition of a zone"""
    args_model = GetNeighborsAtDistanceArgs(start_scenario_id=start_scenario_id, max_distance=max_distance)
    return simulated_map_state.get_neighbors_at_distance(args_model=args_model)

@tool(args_schema=ToolListScenariosClusterSummaryArgs)
def list_scenarios_summary_per_cluster(
    list_all_scenarios_in_each_cluster: bool = False,
    max_scenarios_to_list_per_cluster_if_not_all: Optional[int] = 5,
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None
) -> str:
    """
    (QUERY tool) Summarizes scenario connectivity clusters in the map. A cluster is a group of interconnected scenarios. Lists scenario IDs and names per cluster, either all or a limited sample. Use this tool to list scenarios.
    """
    args_model = ListScenariosClusterSummaryArgs(
        list_all_scenarios_in_each_cluster=list_all_scenarios_in_each_cluster,
        max_scenarios_to_list_per_cluster_if_not_all=max_scenarios_to_list_per_cluster_if_not_all
    )
    assert simulated_map_state is not None, "Injected state not received"
    return simulated_map_state.list_scenarios_summary_per_cluster(args_model=args_model)

@tool(args_schema=ToolFindScenariosArgs)
def find_scenarios_by_attribute(
    attribute_to_filter: Literal["type", "name_contains", "zone", "indoor_or_outdoor"], 
    value_to_match: str, 
    max_results: Optional[int] = 5,
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None
) -> str:
    """(QUERY tool) Finds scenarios matching a given attribute and value. Case-insensitive for 'name_contains'."""
    args_model = FindScenariosArgs(attribute_to_filter=attribute_to_filter, value_to_match=value_to_match, max_results=max_results)
    assert simulated_map_state is not None, "Injected state not received"
    return simulated_map_state.find_scenarios_by_attribute(args_model=args_model)

@tool(args_schema=ToolGetBidirectionalConnectionDetailsArgs)
def get_connection_details(from_scenario_id: str, direction: Direction, simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """
    (QUERY tool) Retrieves details for a specific exit from a given scenario. This includes connection type, travel description, and traversal conditions.
    """
    args_model = GetBidirectionalConnectionDetailsArgs(from_scenario_id=from_scenario_id, direction=direction)
    return simulated_map_state.get_bidirectional_connection_details(args_model=args_model)

@tool(args_schema=ToolGetAvailableExitsArgs)
def get_available_exit_directions(scenario_id: str, simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """
    (QUERY tool) Lists all cardinal directions from a given scenario that do NOT currently have an exit defined. Useful for finding where new connections can be added from this scenario.
    """
    args_model = GetAvailableExitsArgs(scenario_id=scenario_id)
    return simulated_map_state.get_available_exit_directions(args_model=args_model)

@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(justification: str, map_service: Annotated[MapService, InjectedState("map_service")]) -> str:
    """Call this tool ONLY when the simulated map fulfills the objective and all operations are done."""
    args_model = FinalizeSimulationArgs(justification=justification)
    return map_service.finalize_simulation(args_model)

@tool(args_schema=ToolValidateSimulatedMapArgs)
def validate_simulated_map(does_map_meet_criteria: bool, assessment_reasoning: str, suggested_improvements: Optional[str] = None, map_service: Annotated[Optional[MapService], InjectedState("map_service")] = None) -> str:
    """Validates the simulated_map_state. Call it when you are sure that the map either meets all criteria, or that it does not"""
    args_model = ValidateSimulationMapArgs(
        does_map_meet_criteria=does_map_meet_criteria,
        assessment_reasoning=assessment_reasoning,
        suggested_improvements=suggested_improvements
    )
    assert map_service is not None
    return map_service.validate_simulated_map(args_model)


EXECUTORTOOLS = [
        create_scenario,
        modify_scenario,
        delete_scenario,
        create_bidirectional_connection,
        modify_bidirectional_connection,
        delete_bidirectional_connection,
        get_scenario_details,
        get_neighbors_at_distance,
        list_scenarios_summary_per_cluster,
        find_scenarios_by_attribute,
        get_connection_details,
        get_available_exit_directions,
        finalize_simulation
]

VALIDATIONTOOLS = [
        get_neighbors_at_distance,
        list_scenarios_summary_per_cluster,
        find_scenarios_by_attribute,
        get_connection_details,
        get_available_exit_directions,
        validate_simulated_map
]

QUERYTOOLS = [
        get_neighbors_at_distance,
        list_scenarios_summary_per_cluster,
        find_scenarios_by_attribute,
        get_connection_details,
        get_available_exit_directions,
]