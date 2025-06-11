from typing import Dict, List, Any, Optional, Literal, Set, Tuple, Annotated
from pydantic import BaseModel, Field as PydanticField
from langchain_core.tools import tool
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from core_game.map.schemas import Direction, OppositeDirections, ScenarioModel, ConnectionInfo
from subsystems.map.schemas.simulated_map import *


# --- Tools Schemas -- (adding the injected simulated map)
class ToolCreateScenarioArgs(CreateScenarioArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolModifyScenarioArgs(ModifyScenarioArgs):
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")]

class ToolDeleteScenarioArgs(DeleteScenarioArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolCreateBidirectionalConnectionArgs(CreateBidirectionalConnectionArgs):
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")]

class ToolDeleteBidirectionalConnectionArgs(DeleteBidirectionalConnectionArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolModifyBidirectionalConnectionArgs(ModifyBidirectionalConnectionArgs):
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")]

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
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

class ToolValidateSimulatedMapArgs(ValidateSimulationMapArgs):
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]

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
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]
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
    effective_id = simulated_map_state.generate_sequential_scene_id(list(simulated_map_state.simulated_scenarios.keys()))
    try:
        new_scenario_data = {
            "id": effective_id,
            "name": args_model.name,
            "summary_description": args_model.summary_description,
            "visual_description": args_model.visual_description,
            "narrative_context": args_model.narrative_context,
            "indoor_or_outdoor": args_model.indoor_or_outdoor,
            "type": args_model.type,
            "zone": args_model.zone,
            "connections": {},
        }
        new_scenario = ScenarioModel(**new_scenario_data)
        simulated_map_state.simulated_scenarios[effective_id] = new_scenario
        simulated_map_state.island_clusters.append({effective_id})
        return simulated_map_state._log_and_summarize(
            "create_scenario_in_simulation",
            args_model,
            True,
            f"Scenario '{args_model.name}' (ID: {effective_id}) created successfully.",
        )
    except Exception as e:
        return simulated_map_state._log_and_summarize(
            "create_scenario",
            args_model,
            False,
            f"Error while creating scenario: {e}",
        )

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
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None
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
    assert simulated_map_state is not None, "Injected state not received"
    if args_model.scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "modify_scenario",
            args_model,
            False,
            f"Scenario with ID '{args_model.scenario_id}' does not exist.",
        )

    scenario = simulated_map_state.simulated_scenarios[args_model.scenario_id]
    updated_fields = []
    if args_model.new_name is not None:
        scenario.name = args_model.new_name
        updated_fields.append("name")
    if args_model.new_summary_description is not None:
        scenario.summary_description = args_model.new_summary_description
        updated_fields.append("summary_description")
    if args_model.new_visual_description is not None:
        scenario.visual_description = args_model.new_visual_description
        updated_fields.append("visual_description")
    if args_model.new_narrative_context is not None:
        scenario.narrative_context = args_model.new_narrative_context
        updated_fields.append("narrative_context")
    if args_model.new_indoor_or_outdoor is not None:
        scenario.indoor_or_outdoor = args_model.new_indoor_or_outdoor
        updated_fields.append("indoor_or_outdoor")
    if args_model.new_type is not None:
        scenario.type = args_model.new_type
        updated_fields.append("type")
    if args_model.new_zone is not None:
        scenario.zone = args_model.new_zone
        updated_fields.append("zone")
    scenario.was_modified_this_run = True
    return simulated_map_state._log_and_summarize(
        "modify_scenario_in_simulation",
        args_model,
        True,
        f"Scenario '{args_model.scenario_id}' modified. Updated fields: {', '.join(updated_fields) if updated_fields else 'None'}.",
    )

@tool(args_schema=ToolDeleteScenarioArgs)
def delete_scenario(
    scenario_id: str,
    simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]
) -> str:
    """Deletes the specified scenario. An scenario should only be deleted if necessary to complete the task"""
    args_model = DeleteScenarioArgs(
        scenario_id=scenario_id,
    )
    if args_model.scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "delete_scenario",
            args_model,
            False,
            f"Scenario with ID '{args_model.scenario_id}' does not exist.",
        )

    for other_id, other_scenario in simulated_map_state.simulated_scenarios.items():
        for direction, conn_id in other_scenario.connections.items():
            if conn_id:
                conn = simulated_map_state.simulated_connections.get(conn_id)
                if conn and (conn.scenario_a_id == args_model.scenario_id or conn.scenario_b_id == args_model.scenario_id):
                    other_scenario.connections[direction] = None
                    simulated_map_state.simulated_connections.pop(conn_id, None)

    if not simulated_map_state.simulated_scenarios[args_model.scenario_id].was_added_this_run:
        simulated_map_state.deleted_scenarios[args_model.scenario_id] = simulated_map_state.simulated_scenarios[args_model.scenario_id]

    del simulated_map_state.simulated_scenarios[args_model.scenario_id]
    simulated_map_state._compute_island_clusters()

    return simulated_map_state._log_and_summarize(
        "delete_scenario",
        args_model,
        True,
        f"Scenario '{args_model.scenario_id}' deleted successfully.",
    )

@tool(args_schema=ToolCreateBidirectionalConnectionArgs)
def create_bidirectional_connection(
    from_scenario_id: str, 
    direction_from_origin: Direction, 
    to_scenario_id: str, 
    connection_type: str, 
    travel_description: Optional[str] = None, 
    traversal_conditions: Optional[List[str]] = None,
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None
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
    assert simulated_map_state is not None, "Injected state not received"

    if args_model.from_scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "create_bidirectional_connection",
            args_model,
            False,
            f"Error: Origin scenario ID '{args_model.from_scenario_id}' not fpund.",
        )
    if args_model.to_scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "create_bidirectional_connection",
            args_model,
            False,
            f"Error: Destination scenario ID '{args_model.to_scenario_id}' not found.",
        )
    if args_model.from_scenario_id == args_model.to_scenario_id:
        return simulated_map_state._log_and_summarize(
            "create_bidirectional_connection",
            args_model,
            False,
            "Error: Cannot connect a scenario to itself.",
        )

    origin_scenario = simulated_map_state.simulated_scenarios[args_model.from_scenario_id]
    destination_scenario = simulated_map_state.simulated_scenarios[args_model.to_scenario_id]

    for existing_direction, conn_id in origin_scenario.connections.items():
        if conn_id:
            conn = simulated_map_state.simulated_connections.get(conn_id)
            if conn and ((conn.scenario_a_id == args_model.from_scenario_id and conn.scenario_b_id == args_model.to_scenario_id) or
                         (conn.scenario_b_id == args_model.from_scenario_id and conn.scenario_a_id == args_model.to_scenario_id)):
                return simulated_map_state._log_and_summarize(
                    "create_bidirectional_connection",
                    args_model,
                    False,
                    f"Error: Origin '{args_model.from_scenario_id}' has an existing connection via direction '{existing_direction}' to '{args_model.to_scenario_id}'. Cannot create another connection between them.",
                )

    direction_to_origin = OppositeDirections[args_model.direction_from_origin]

    if origin_scenario.connections.get(args_model.direction_from_origin) is not None:
        return simulated_map_state._log_and_summarize(
            "create_bidirectional_connection",
            args_model,
            False,
            f"Error: Origin scenario '{args_model.from_scenario_id}' already has an exit to the '{args_model.direction_from_origin}'.",
        )
    if destination_scenario.connections.get(direction_to_origin) is not None:
        return simulated_map_state._log_and_summarize(
            "create_bidirectional_connection",
            args_model,
            False,
            f"Error: Destination scenario '{args_model.to_scenario_id}' already has an exit to its '{direction_to_origin}' (which would be the return path).",
        )

    connection_id = simulated_map_state.generate_sequential_connection_id(list(simulated_map_state.simulated_connections.keys()))
    connection = ConnectionInfo(
        id=connection_id,
        scenario_a_id=args_model.from_scenario_id,
        scenario_b_id=args_model.to_scenario_id,
        direction_from_a=args_model.direction_from_origin,
        connection_type=args_model.connection_type,
        travel_description=args_model.travel_description,
        traversal_conditions=args_model.traversal_conditions or [],
    )
    simulated_map_state.simulated_connections[connection_id] = connection
    origin_scenario.connections[args_model.direction_from_origin] = connection_id
    destination_scenario.connections[direction_to_origin] = connection_id

    simulated_map_state._compute_island_clusters()
    return simulated_map_state._log_and_summarize(
        "create_bidirectional_connection",
        args_model,
        True,
        f"Connection type'{args_model.connection_type}' created: '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) <-> '{args_model.to_scenario_id}' ({direction_to_origin}).",
    )


@tool(args_schema=ToolDeleteBidirectionalConnectionArgs)
def delete_bidirectional_connection(scenario_id_A: str, direction_from_A: Direction, simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""
    args_model = DeleteBidirectionalConnectionArgs(scenario_id_A=scenario_id_A, direction_from_A=direction_from_A)
    if args_model.scenario_id_A not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "delete_bidirectional_connection",
            args_model,
            False,
            f"Error: Scenario A ID '{args_model.scenario_id_A}' not found.",
        )

    scenario_A = simulated_map_state.simulated_scenarios[args_model.scenario_id_A]
    conn_id_A_to_B = scenario_A.connections.get(args_model.direction_from_A)
    conn = simulated_map_state.simulated_connections.get(conn_id_A_to_B) if conn_id_A_to_B else None

    if conn is None:
        return simulated_map_state._log_and_summarize(
            "delete_bidirectional_connection",
            args_model,
            False,
            f"Error: Scenario '{args_model.scenario_id_A}' has no connection to the '{args_model.direction_from_A}'.",
        )

    scenario_id_B = conn.scenario_b_id if conn.scenario_a_id == args_model.scenario_id_A else conn.scenario_a_id
    if scenario_id_B not in simulated_map_state.simulated_scenarios:
        scenario_A.connections[args_model.direction_from_A] = None
        simulated_map_state.simulated_connections.pop(conn.id, None)
        simulated_map_state._compute_island_clusters()
        return simulated_map_state._log_and_summarize(
            "delete_bidirectional_connection",
            args_model,
            True,
            f"Exit from '{args_model.scenario_id_A}' ({args_model.direction_from_A}) cleared. Target scenario '{scenario_id_B}' was not found (map was possibly inconsistent).",
        )

    scenario_B = simulated_map_state.simulated_scenarios[scenario_id_B]
    direction_from_B = OppositeDirections[args_model.direction_from_A]

    scenario_A.connections[args_model.direction_from_A] = None
    conn_B_id = scenario_B.connections.get(direction_from_B)
    if conn_B_id and conn_B_id == conn.id:
        scenario_B.connections[direction_from_B] = None
        simulated_map_state.simulated_connections.pop(conn.id, None)
        message = f"Bidirectional connection '{args_model.scenario_id_A}' ({args_model.direction_from_A}) <-> '{scenario_id_B}' ({direction_from_B}) deleted."
    else:
        simulated_map_state.simulated_connections.pop(conn.id, None)
        message = f"Connection from '{args_model.scenario_id_A}' ({args_model.direction_from_A}) to '{scenario_id_B}' deleted. Reverse connection from '{scenario_id_B}' not found or not pointing back as expected."

    simulated_map_state._compute_island_clusters()
    return simulated_map_state._log_and_summarize(
        "delete_bidirectional_connection",
        args_model,
        True,
        message,
    )

@tool(args_schema=ToolModifyBidirectionalConnectionArgs)
def modify_bidirectional_connection( 
    from_scenario_id: str, 
    direction_from_origin: Direction,
    new_connection_type: Optional[str] = None,
    new_travel_description: Optional[str] = None,
    new_traversal_conditions: Optional[List[str]] = None,
    simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None
) -> str:
    """Modifies attributes of an existing bidirectional connection. Only provided attributes are changed."""
    
    args_model = ModifyBidirectionalConnectionArgs(
        from_scenario_id=from_scenario_id, 
        direction_from_origin=direction_from_origin,
        new_connection_type=new_connection_type, 
        new_travel_description=new_travel_description,
        new_traversal_conditions=new_traversal_conditions
    )
    assert simulated_map_state is not None, "Injected state not received"

    if args_model.from_scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "modify_bidirectional_connection",
            args_model,
            False,
            f"Error: Origin scenario ID '{args_model.from_scenario_id}' not found.",
        )

    origin_scenario = simulated_map_state.simulated_scenarios[args_model.from_scenario_id]
    conn_id_origin = origin_scenario.connections.get(args_model.direction_from_origin)
    conn_origin = simulated_map_state.simulated_connections.get(conn_id_origin) if conn_id_origin else None

    if conn_origin is None:
        return simulated_map_state._log_and_summarize(
            "modify_bidirectional_connection",
            args_model,
            False,
            f"Error: Scenario '{args_model.from_scenario_id}' has no connection to the '{args_model.direction_from_origin}'.",
        )

    to_scenario_id = conn_origin.scenario_b_id if conn_origin.scenario_a_id == args_model.from_scenario_id else conn_origin.scenario_a_id
    if to_scenario_id not in simulated_map_state.simulated_scenarios:
        return simulated_map_state._log_and_summarize(
            "modify_bidirectional_connection",
            args_model,
            False,
            f"Exit from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) points to target scenario '{to_scenario_id}' not found.",
        )

    destination_scenario = simulated_map_state.simulated_scenarios[to_scenario_id]
    direction_to_origin = OppositeDirections[args_model.direction_from_origin]
    conn_id_destination = destination_scenario.connections.get(direction_to_origin)
    conn_destination = simulated_map_state.simulated_connections.get(conn_id_destination) if conn_id_destination else None

    updated_fields_origin = []
    if args_model.new_connection_type is not None:
        conn_origin.connection_type = args_model.new_connection_type
        updated_fields_origin.append("connection_type")
    if args_model.new_travel_description is not None:
        conn_origin.travel_description = args_model.new_travel_description
        updated_fields_origin.append("travel_description")
    if args_model.new_traversal_conditions is not None:
        conn_origin.traversal_conditions = args_model.new_traversal_conditions
        updated_fields_origin.append("traversal_conditions")

    if conn_destination and (conn_destination.scenario_a_id == to_scenario_id and conn_destination.scenario_b_id == args_model.from_scenario_id or
                             conn_destination.scenario_b_id == to_scenario_id and conn_destination.scenario_a_id == args_model.from_scenario_id):
        if args_model.new_connection_type is not None:
            conn_destination.connection_type = args_model.new_connection_type
        if args_model.new_traversal_conditions is not None:
            conn_destination.traversal_conditions = args_model.new_traversal_conditions
        if args_model.new_travel_description is not None:
            conn_destination.travel_description = args_model.new_travel_description
        message = (
            f"Bidirectional connection from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) <-> '{to_scenario_id}' ({direction_to_origin}) modified. Updated fields: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
        )
    else:
        message = (
            f"Connection from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) modified. Reverse connection from '{to_scenario_id}' not found or not pointing back as expected. Updated fields on forward path: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
        )

    return simulated_map_state._log_and_summarize(
        "modify_bidirectional_connection",
        args_model,
        True,
        message,
    )

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
def finalize_simulation(justification: str, simulated_map_state: Annotated[SimulatedMapModel, InjectedState("working_simulated_map")]) -> str:
    """Call this tool ONLY when the simulated map fulfills the objective and all operations are done."""
    args_model = FinalizeSimulationArgs(justification=justification)
    simulated_map_state._compute_island_clusters()
    simulated_map_state.task_finalized_by_agent = True
    simulated_map_state.task_finalized_justification = args_model.justification
    return simulated_map_state._log_and_summarize(
        "finalize_simulation",
        args_model,
        True,
        "Simulation finalized.",
    )

@tool(args_schema=ToolValidateSimulatedMapArgs)
def validate_simulated_map(does_map_meet_criteria: bool, assessment_reasoning: str, suggested_improvements: Optional[str] = None, simulated_map_state: Annotated[Optional[SimulatedMapModel], InjectedState("working_simulated_map")] = None) -> str:
    """Validates the simulated_map_state. Call it when you are sure that the map either meets all criteria, or that it does not"""
    args_model = ValidateSimulationMapArgs(
        does_map_meet_criteria=does_map_meet_criteria,
        assessment_reasoning=assessment_reasoning,
        suggested_improvements=suggested_improvements
    )
    assert simulated_map_state is not None
    simulated_map_state.agent_validated = True
    simulated_map_state.agent_validation_conclusion_flag = args_model.does_map_meet_criteria
    simulated_map_state.agent_validation_assessment_reasoning = args_model.assessment_reasoning
    if args_model.suggested_improvements:
        simulated_map_state.agent_validation_suggested_improvements = args_model.suggested_improvements
    else:
        simulated_map_state.agent_validation_suggested_improvements = ""
    if simulated_map_state.agent_validation_conclusion_flag:
        return simulated_map_state._log_and_summarize(
            "validate_simulated_map",
            args_model,
            True,
            f"Simulated map meets all criteria. Reason: {args_model.assessment_reasoning}",
        )
    else:
        return simulated_map_state._log_and_summarize(
            "validate_simulated_map",
            args_model,
            True,
            f"Simulated doesn't meet all criteria. Reason: {args_model.assessment_reasoning}. Suggestions: {simulated_map_state.agent_validation_suggested_improvements}",
        )


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