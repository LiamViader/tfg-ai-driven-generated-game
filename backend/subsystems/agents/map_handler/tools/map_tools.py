from typing import Dict, List, Any, Optional, Literal, Set, Tuple, Annotated
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
from langgraph.types import Command
from langchain_core.messages import ToolMessage

from core_game.map.schemas import Direction, OppositeDirections
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS

from simulated.game_state import SimulatedGameStateSingleton
from subsystems.agents.map_handler.tools.helpers import get_observation
from langgraph.prebuilt import InjectedState
from subsystems.agents.utils.schemas import InjectedToolContext
from subsystems.agents.utils.logs import get_log_item, extract_tool_args

# --- Tools Schemas --
class ToolCreateScenarioArgs(InjectedToolContext):
    name: str = Field(..., description=SCENARIO_FIELDS["name"])
    summary_description: str = Field(..., description=SCENARIO_FIELDS["summary_description"])
    visual_description: str = Field(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = Field(..., description=SCENARIO_FIELDS["narrative_context"])
    indoor_or_outdoor: Literal["indoor", "outdoor"] = Field(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = Field(..., description=SCENARIO_FIELDS["type"])
    zone: str = Field(..., description=SCENARIO_FIELDS["zone"])

class ToolModifyScenarioArgs(InjectedToolContext):
    scenario_id: str = Field(..., description="ID of the scenario to modify.")
    new_name: Optional[str] = Field(None, description=SCENARIO_FIELDS["name"])
    new_summary_description: Optional[str] = Field(None, description=SCENARIO_FIELDS["summary_description"])
    new_visual_description: Optional[str] = Field(None, description=SCENARIO_FIELDS["visual_description"])
    new_narrative_context: Optional[str] = Field(None, description=SCENARIO_FIELDS["narrative_context"])
    new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = Field(None, description=SCENARIO_FIELDS["indoor_or_outdoor"])
    new_type: Optional[str] = Field(None, description=SCENARIO_FIELDS["type"])
    new_zone: Optional[str] = Field(None, description=SCENARIO_FIELDS["zone"])


class ToolDeleteScenarioArgs(InjectedToolContext):
    scenario_id: str = Field(..., description="ID of the scenario to delete.")


class ToolCreateBidirectionalConnectionArgs(InjectedToolContext):
    scenario_id_A: str = Field(..., description="ID of scenario A.")
    direction_from_A: Direction = Field(..., description="Direction of the exit from scenario A.")
    scenario_id_B: str = Field(..., description="ID of scenario B.")
    connection_type: str = Field(..., description=EXIT_FIELDS["connection_type"])
    travel_description: Optional[str] = Field(None, description=EXIT_FIELDS["travel_description"])
    traversal_conditions: List[str] = Field(default_factory=list, description=EXIT_FIELDS["traversal_conditions"])

class ToolDeleteBidirectionalConnectionArgs(InjectedToolContext):
    scenario_id_A: str = Field(..., description="ID of one scenario in the connection.")
    direction_from_A: Direction = Field(..., description="Direction of the exit from scenario A that identifies the connection leg to delete.")


class ToolModifyBidirectionalConnectionArgs(InjectedToolContext):
    scenario_id_A: str = Field(..., description="ID of one scenario in the connection.")
    direction_from_A: Direction = Field(..., description="Direction of the exit from scenario A that identifies the connection leg to modify.")
    new_connection_type: Optional[str] = Field(None, description="New type for the connection.")
    new_travel_description: Optional[str] = Field(None, description="New travel description for the path.")
    new_traversal_conditions: Optional[List[str]] = Field(None, description="New traversal conditions for the connection.")


class ToolGetScenarioDetailsArgs(InjectedToolContext):
    scenario_id: str = Field(..., description="ID of the scenario for which to retrieve details.")


class ToolGetNeighborsAtDistanceArgs(InjectedToolContext):
    start_scenario_id: str = Field(..., description="ID of the scenario from which to start the search.")
    max_distance: int = Field(..., description="Maximum distance (number of hops) to explore. Recommended 2-3.", ge=1, le=4)


class ToolListScenariosClusterSummaryArgs(InjectedToolContext):
    list_all_scenarios_in_each_cluster: bool = Field(
        default=False,  # Default gives a summary
        description="If true, lists all scenarios (ID and name) in each cluster. If false (default), shows a limited preview per cluster. Use true only in limited justified ocasions"
    )
    max_scenarios_to_list_per_cluster_if_not_all: Optional[int] = Field(
        default=5,
        description="Max number of scenarios to show per cluster when not listing all. Ignored if 'list_all_scenarios_in_each_cluster' is True."
    )


class ToolFindScenariosArgs(InjectedToolContext):
    attribute_to_filter: Literal["type", "zone", "name_contains", "indoor_or_outdoor"] = Field(..., description="Attribute to filter by.")
    value_to_match: str = Field(..., description="Value the attribute should match or contain.")
    max_results: Optional[int] = Field(5, description="Maximum number of matching scenarios to return.")


class ToolGetBidirectionalConnectionDetailsArgs(InjectedToolContext): 
    from_scenario_id: str = Field(..., description="ID of the scenario from which the exit originates.")
    direction: Direction = Field(..., description="Direction of the exit whose details are requested.")


class ToolGetAvailableExitsArgs(InjectedToolContext):
    scenario_id: str = Field(..., description="ID of the scenario to check for available exit directions.")


class ToolFinalizeSimulationArgs(InjectedToolContext):
    justification: str = Field(..., description="Justification of why the simulated map meets all criteria.")


class ToolValidateSimulatedMapArgs(InjectedToolContext):
    does_map_meet_criteria: bool = Field(..., description="Your assessment: set to True if you believe the map successfully meets all current objectives and constraints; False otherwise.")
    assessment_reasoning: str = Field(..., description="Your concise justification explaining why the map meets (or fails to meet) the objectives and constraints.")
    suggested_improvements: Optional[str] = Field(default=None, description="If `does_map_meet_criteria` is False, provide specific, actionable suggestions on how the map can be modified or updated to meet the unmet criteria. If True, this field can be omitted.")


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
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Creates a new scenario in the simulated map."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    scenario=simulated_state.create_scenario(
        name=name,
        narrative_context=narrative_context,
        visual_description=visual_description,
        summary_description=summary_description,
        indoor_or_outdoor=indoor_or_outdoor,
        type=type,
        zone=zone
    )

    return Command(update={
        logs_field_to_update: [get_log_item("create_scenario", args, False, True, f"Scenario '{scenario.name}' (ID: {scenario.id}) created successfully.")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "create_scenario", True, f"Scenario '{scenario.name}' (ID: {scenario.id}) created successfully."),
                tool_call_id=tool_call_id
            )
        ]
    })
    


@tool(args_schema=ToolModifyScenarioArgs)
def modify_scenario(
    scenario_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    new_name: Optional[str] = None,
    new_summary_description: Optional[str] = None,
    new_visual_description: Optional[str] = None,
    new_narrative_context: Optional[str] = None,
    new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = None,
    new_type: Optional[str] = None,
    new_zone: Optional[str] = None,
) -> Command:
    """Modifies the specified scenario. Only the provided fields will be updated."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()

    updated_fields = []
    if new_name is not None:
        updated_fields.append("name")
    if new_summary_description is not None:
        updated_fields.append("summary_description")
    if new_visual_description is not None:
        updated_fields.append("visual_description")
    if new_narrative_context is not None:
        updated_fields.append("narrative_context")
    if new_indoor_or_outdoor is not None:
        updated_fields.append("indoor_or_outdoor")
    if new_type is not None:
        updated_fields.append("type")
    if new_zone is not None:
        updated_fields.append("zone")

    message = f"Scenario '{scenario_id}' modified. Updated fields: {', '.join(updated_fields) if updated_fields else 'None'}."

    if simulated_state.modify_scenario(scenario_id):
        return Command(update={
            logs_field_to_update: [get_log_item("modify_scenario", args, False, True, message)],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "modify_scenario", True, message),
                    tool_call_id=tool_call_id
                )
            ]
        })
    else:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_scenario", args, False, False, f"Scenario with ID '{scenario_id}' does not exist.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "modify_scenario", False, f"Scenario with ID '{scenario_id}' does not exist."),
                    tool_call_id=tool_call_id
                )
            ]
        })

@tool(args_schema=ToolDeleteScenarioArgs)
def delete_scenario(
    scenario_id: str,
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Deletes the specified scenario. An scenario should only be deleted if necessary to complete the task"""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    try:
        scenario = simulated_state.delete_scenario(scenario_id)
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("delete_scenario", args, False, False, str(e))],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "delete_scenario", False, str(e)),
                    tool_call_id=tool_call_id
                )
            ]
        })
    return Command(update={
        logs_field_to_update: [get_log_item("delete_scenario", args, False, True, f"Scenario '{scenario_id}' deleted successfully.")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "delete_scenario", True, f"Scenario '{scenario_id}' deleted successfully."),
                tool_call_id=tool_call_id
            )
        ]
    })
    

@tool(args_schema=ToolCreateBidirectionalConnectionArgs)
def create_bidirectional_connection(
    scenario_id_A: str, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    direction_from_A: Direction, 
    scenario_id_B: str, 
    connection_type: str, 
    travel_description: Optional[str] = None, 
    traversal_conditions: Optional[List[str]] = None,
) -> Command:
    """Creates a bidirectional connection from the origin scenario to the destination in the specified direction, and from the destination back to the origin in the opposite direction. Both directions must be unoccupied (i.e., no existing exits); otherwise, the connection will not be created and an error observation will be returned."""


    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()

    try:
        connection = simulated_state.create_bidirectional_connection(scenario_id_A,direction_from_A,scenario_id_B,connection_type,travel_description,traversal_conditions)
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("create_bidirectional_connection", args, False, False, str(e))],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "create_bidirectional_connection", False, str(e)),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    message = f"Connection '{connection.connection_type}' created: '{scenario_id_A}' ({direction_from_A}) <-> '{scenario_id_B}' ({OppositeDirections[direction_from_A]})."

    return Command(update={
        logs_field_to_update: [get_log_item("create_bidirectional_connection", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "create_bidirectional_connection", True, message),
                tool_call_id=tool_call_id
            )
        ]
    })


@tool(args_schema=ToolDeleteBidirectionalConnectionArgs)
def delete_bidirectional_connection(
    scenario_id_A: str, 
    direction_from_A: Direction, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    
    connection_info = simulated_state.get_connection(scenario_id_A, direction_from_A)

    if not connection_info:
        return Command(update={
            logs_field_to_update: [get_log_item("delete_bidirectional_connection", args, False, False, f"No connection found from '{scenario_id_A}' in direction '{direction_from_A}'.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "delete_bidirectional_connection", False, f"No connection found from '{scenario_id_A}' in direction '{direction_from_A}'."),
                    tool_call_id=tool_call_id
                )
            ]
        })

    try:
        message=simulated_state.delete_bidirectional_connection(scenario_id_A, direction_from_A)
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("delete_bidirectional_connection", args, False, False, str(e))],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "delete_bidirectional_connection", False, str(e)),
                    tool_call_id=tool_call_id
                )
            ]
        })

    message = f"Bidirectional connection '{scenario_id_A}' ({direction_from_A}) <-> '{connection_info.get_other_scenario_id(scenario_id_A)}' ({connection_info.get_direction_to(direction_from_A)}) deleted."

    return Command(update={
        logs_field_to_update: [get_log_item("delete_bidirectional_connection", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "delete_bidirectional_connection", True, message),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolModifyBidirectionalConnectionArgs)
def modify_bidirectional_connection(
    scenario_id_A: str, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId],
    direction_from_A: Direction,
    new_connection_type: Optional[str] = None,
    new_travel_description: Optional[str] = None,
    new_traversal_conditions: Optional[List[str]] = None
) -> Command:
    """Modifies attributes of an existing bidirectional connection. Only provided attributes are changed."""
    
    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()

    updated_fields = []
    if new_connection_type is not None:
        updated_fields.append("connection_type")
    if new_travel_description is not None:
        updated_fields.append("travel_description")
    if new_traversal_conditions is not None:
        updated_fields.append("traversal_conditions")

    try:
        simulated_state.modify_bidirectional_connection(
            from_scenario_id=scenario_id_A,
            direction_from_origin=direction_from_A,
            new_connection_type=new_connection_type,
            new_travel_description=new_travel_description,
            new_traversal_conditions=new_traversal_conditions
        )
    except Exception as e:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_bidirectional_connection", args, False, False, str(e))],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "modify_bidirectional_connection", False, str(e)),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    connection_info= simulated_state.get_connection(scenario_id_A, direction_from_A)

    if not connection_info:
        return Command(update={
            logs_field_to_update: [get_log_item("modify_bidirectional_connection", args, False, False, f"No connection found from '{scenario_id_A}' in direction '{direction_from_A}'.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "modify_bidirectional_connection", False, f"No connection found from '{scenario_id_A}' in direction '{direction_from_A}'."),
                    tool_call_id=tool_call_id
                )
            ]
        })

    message = f"Bidirectional connection from '{scenario_id_A}' ({direction_from_A}) <-> '{connection_info.get_other_scenario_id(scenario_id_A)}' ({connection_info.get_direction_to(scenario_id_A)}) modified. Updated fields: {', '.join(updated_fields) if updated_fields else 'None'}."

    return Command(update={
        logs_field_to_update: [get_log_item("modify_bidirectional_connection", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "modify_bidirectional_connection", True, message),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolGetScenarioDetailsArgs)
def get_scenario_details(
    scenario_id: str, 
    messages_field_to_update: 
    Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """(QUERY tool) Retrieves and returns all details for a specific scenario in the simulated map."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    scenario = simulated_state.find_scenario(scenario_id)
    if not scenario:
        return Command(update={
            logs_field_to_update: [get_log_item("get_scenario_details", args, True, False, f"Scenario with ID '{scenario_id}' does not exist.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_scenario_details", False, f"Scenario with ID '{scenario_id}' does not exist."),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    details_str = f"Details for Scenario: {scenario.id}:\n"
    details_str += f"  ID: {scenario.id}\n"
    details_str += f"  Name: {scenario.name}\n"
    details_str += f"  Type: {scenario.type}\n"
    details_str += f"  Zone: {scenario.zone}\n"
    details_str += f"  Indoor or outdoor: {scenario.indoor_or_outdoor}\n"
    details_str += f"  Summary Description: {scenario.summary_description}\n"
    details_str += f"  Visual Description: {scenario.visual_description}\n"
    details_str += f"  Narrative Context: {scenario.narrative_context}\n"
    details_str +=  "  Connections:\n"
    if any(conn_id for conn_id in scenario.connections.values()):
        for direction, conn_id in scenario.connections.items():
            if conn_id:
                conn = simulated_state.get_connection(scenario.id, direction)
                if conn:
                    other_id = conn.get_other_scenario_id(scenario.id)
                    details_str += (
                        f"    - {direction}: to '{other_id}' (Connection type: {conn.connection_type}, "
                        f"Conditions: {conn.traversal_conditions}, Travel: \"{conn.travel_description}\")\n"
                    )
            else:
                details_str += f"    - {direction}: (None)\n"
    else:
        details_str += "    (No connections defined)\n"

    return Command(update={
        logs_field_to_update: [get_log_item("get_scenario_details", args, True, True, details_str)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "get_scenario_details", True, details_str),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolGetNeighborsAtDistanceArgs)
def get_neighbors_at_distance(
    start_scenario_id: str,
    max_distance: int, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """(QUERY tool) Retrieves scenarios within N hops from a starting scenario, including connection details. Use this to understand spatial composition"""
        
    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    scenario = simulated_state.find_scenario(start_scenario_id)
    if not scenario:
        return Command(update={
            logs_field_to_update: [get_log_item("get_neighbors_at_distance", args, True, False, f"Start scenario with ID '{start_scenario_id}' does not exist.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_neighbors_at_distance", False, f"Start scenario with ID '{start_scenario_id}' does not exist."),
                    tool_call_id=tool_call_id
                )
            ]
        })

    output_lines = [f"Neighbors of '{scenario.name}' (ID: {scenario.id}) up to distance {max_distance}:"]
    # BFS: (scenario_id, current_distance, path_description_list)
    queue: List[Tuple[str, int, List[str]]] = [(scenario.id, 0, [])]
    # Visited format: {scenario_id: distance_found_at} to find shortest paths
    visited_at_dist: Dict[str, int] = {scenario.id: 0}
    
    results_by_distance: Dict[int, List[str]] = {dist: [] for dist in range(1, max_distance + 1)}

    head = 0
    while head < len(queue):
        current_id, distance, _ = queue[head] 
        head += 1

        if distance >= max_distance: continue

        current_scenario = simulated_state.find_scenario(current_id)
        if not current_scenario or not current_scenario.connections:
            continue

        for direction, conn_id in current_scenario.connections.items():
            if conn_id:
                conn = simulated_state.get_connection(current_id, direction)
                if conn is None:
                    continue
                neighbor_id = conn.get_other_scenario_id(current_id)
                neighbor_scenario = simulated_state.find_scenario(neighbor_id)
                if neighbor_scenario:
                    # Process if not visited, or found via a shorter/equal path to add all connections at this distance
                    if neighbor_id not in visited_at_dist or visited_at_dist[neighbor_id] >= distance + 1:
                        if neighbor_id not in visited_at_dist : # Add to queue only if truly new or shorter path (for BFS structure)
                            visited_at_dist[neighbor_id] = distance + 1
                            if distance + 1 < max_distance : # Only add to queue if we need to explore further from it
                                queue.append((neighbor_id, distance + 1, []))

                    if visited_at_dist[neighbor_id] == distance + 1:  # ensure we only list it once per distance level from different paths
                        connection_desc = f"from '{current_scenario.name}' (ID: {current_id}) via '{direction}' (connection type: {conn.connection_type})"
                        entry_str = f"- '{neighbor_scenario.name}' (ID: {neighbor_id}, Type: {neighbor_scenario.type}, Zone: {neighbor_scenario.zone}) reached {connection_desc}."
                        if entry_str not in results_by_distance[distance + 1]:  # Avoid duplicate entries if multiple paths lead at same shortest distance
                            results_by_distance[distance + 1].append(entry_str)
    
    has_results = False
    for dist_level in range(1, max_distance + 1):
        if results_by_distance[dist_level]:
            has_results = True
            output_lines.append(f"Distance {dist_level}:")
            output_lines.extend(sorted(results_by_distance[dist_level]))

    if not has_results:
        output_lines.append("(No neighbors found within this specified distance via explored paths).")
    return Command(update={
        logs_field_to_update: [get_log_item("get_neighbors_at_distance", args, True, True, "\n".join(output_lines))],
        messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_neighbors_at_distance", True, "\n".join(output_lines)),
                    tool_call_id=tool_call_id
                )
            ]
        })

@tool(args_schema=ToolListScenariosClusterSummaryArgs)
def list_scenarios_summary_per_cluster(
    tool_call_id: Annotated[str, InjectedToolCallId],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    list_all_scenarios_in_each_cluster: bool = False,
    max_scenarios_to_list_per_cluster_if_not_all: Optional[int] = 5,
) -> Command:
    """
    (QUERY tool) Summarizes scenario connectivity clusters in the map. A cluster is a group of interconnected scenarios. Lists scenario IDs and names per cluster, either all or a limited sample. Use this tool to list scenarios.
    """

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    if simulated_state.get_scenario_count()<=0:
        return Command(update={
            logs_field_to_update: [get_log_item("list_scenarios_summary_per_cluster", args, True, True, "The simulated map is currently empty. No clusters to display.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "list_scenarios_summary_per_cluster", True, "The simulated map is currently empty. No clusters to display."),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    summary_text = simulated_state.get_cluster_summary(
        list_all_scenarios=list_all_scenarios_in_each_cluster,
        max_listed_per_cluster=max_scenarios_to_list_per_cluster_if_not_all
    )

    return Command(update={
        logs_field_to_update: [get_log_item("list_scenarios_summary_per_cluster", args, True, True, f"Current map connectivity cluster summary:\n{summary_text}")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "list_scenarios_summary_per_cluster", True, f"Current map connectivity cluster summary:\n{summary_text}"),
                tool_call_id=tool_call_id
            )
        ]
    })


@tool(args_schema=ToolFindScenariosArgs)
def find_scenarios_by_attribute(
    tool_call_id: Annotated[str, InjectedToolCallId],
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")],
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    attribute_to_filter: Literal["type", "name_contains", "zone", "indoor_or_outdoor"], 
    value_to_match: str, 
    max_results: Optional[int] = 5,
) -> Command:
    """(QUERY tool) Finds scenarios matching a given attribute and value. Case-insensitive for 'name_contains'."""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    matches = simulated_state.find_scenarios_by_attribute(attribute_to_filter,value_to_match)
    matches_strings = []
    for scenario in matches:
        if len(matches) >= (max_results or 5): break

        if attribute_to_filter == "type":
            matches_strings.append(f'- ID: {scenario.id}, Name: "{scenario.name}", Type: {scenario.type}')
        elif attribute_to_filter == "indoor_or_outdoor" :
            matches_strings.append(f'- ID: {scenario.id}, Name: "{scenario.name}", {scenario.indoor_or_outdoor}')
        elif attribute_to_filter == "name_contains":
            matches_strings.append(f'- ID: {scenario.id}, Name: "{scenario.name}"')
        elif attribute_to_filter == "zone":
            matches_strings.append(f'- ID: {scenario.id}, Name: "{scenario.name}", Zone: "{scenario.zone}"')
    
    if not matches_strings:
        return Command(update={
            logs_field_to_update: [get_log_item("find_scenarios_by_attribute", args, True, True, f"No scenarios found matching '{attribute_to_filter}' with value '{value_to_match}'.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "find_scenarios_by_attribute", True, f"No scenarios found matching '{attribute_to_filter}' with value '{value_to_match}'."),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    return Command(update={
        logs_field_to_update: [get_log_item("find_scenarios_by_attribute", args, True, True, f"Scenarios matching '{attribute_to_filter}' with value '{value_to_match}':\n" + "\n".join(matches_strings))],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "find_scenarios_by_attribute", True, f"Scenarios matching '{attribute_to_filter}' with value '{value_to_match}':\n" + "\n".join(matches_strings)),
                tool_call_id=tool_call_id
            )
        ]
    })


@tool(args_schema=ToolGetBidirectionalConnectionDetailsArgs)
def get_connection_details(
    from_scenario_id: str, 
    direction: Direction, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    (QUERY tool) Retrieves details for a specific exit from a given scenario. This includes connection type, travel description, and traversal conditions.
    """
    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    scenario = simulated_state.find_scenario(from_scenario_id)
    if not scenario:
        return Command(update={
            logs_field_to_update: [get_log_item("get_connection_details", args, True, False, f"Scenario with ID '{from_scenario_id}' does not exist.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_connection_details", False, f"Scenario with ID '{from_scenario_id}' does not exist."),
                    tool_call_id=tool_call_id
                )
            ]
        })

    conn = simulated_state.get_connection(from_scenario_id,direction)

    if conn is None:
        return Command(update={
            logs_field_to_update: [get_log_item("get_connection_details", args, True, False, f"Scenario '{from_scenario_id}' has no connection defined in the direction '{direction}'.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_connection_details", False, f"Scenario '{from_scenario_id}' has no connection defined in the direction '{direction}'."),
                    tool_call_id=tool_call_id
                )
            ]
        })

    target_id = conn.get_other_scenario_id(from_scenario_id)
    details_str = (
        f"Details for connection from '{from_scenario_id}' towards '{direction}':\n"
        f"  - Leads to Scenario ID: {target_id}\n"
        f"  - Connection Type: {conn.connection_type}\n"
        f"  - Travel Description: {conn.travel_description or 'N/A'}\n"
        f"  - Traversal Conditions: {', '.join(conn.traversal_conditions) if conn.traversal_conditions else 'None'}"
    )
    return Command(update={
        logs_field_to_update: [get_log_item("get_connection_details", args, True, True, details_str)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "get_connection_details", True, details_str),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolGetAvailableExitsArgs)
def get_available_exit_directions(
    scenario_id: str, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """
    (QUERY tool) Lists all cardinal directions from a given scenario that do NOT currently have an exit defined. Useful for finding where new connections can be added from this scenario.
    """
    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    scenario = simulated_state.find_scenario(scenario_id)
    if not scenario:
        return Command(update={
            logs_field_to_update: [get_log_item("get_available_exit_directions", args, True, False, f"Scenario with ID '{scenario_id}' does not exist.")],
            messages_field_to_update: [
                ToolMessage(
                    get_observation(simulated_state.get_scenario_count(), "get_available_exit_directions", False, f"Scenario with ID '{scenario_id}' does not exist."),
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    available_directions = [
        direction for direction in Direction.__args__  # type: ignore
        if scenario.connections.get(direction) is None
    ]

    if not available_directions:
        message = f"Scenario '{scenario.name}' (ID: {scenario_id}) has no available (empty) directions; all are occupied or there are no slots."
    else:
        message = f"Available (empty) directions for scenario '{scenario.name}' (ID: {scenario_id}): {', '.join(available_directions)}."

    return Command(update={
        logs_field_to_update: [get_log_item("get_available_exit_directions", args, True, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "get_available_exit_directions", True, message),
                tool_call_id=tool_call_id
            )
        ]
    })

@tool(args_schema=ToolFinalizeSimulationArgs)
def finalize_simulation(
    justification: str, 
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Call this tool ONLY when the simulated map fulfills the objective and all operations are done."""
    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    return Command(update={
        logs_field_to_update: [get_log_item("finalize_simulation", args, False, True, "Simulation finalized.")],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "finalize_simulation", True, "Simulation finalized."),
                tool_call_id=tool_call_id
            )
        ],
        "map_task_finalized_by_agent": True,
        "map_task_finalized_justification": justification
    })

@tool(args_schema=ToolValidateSimulatedMapArgs)
def validate_simulated_map(
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")], 
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")],
    tool_call_id: Annotated[str, InjectedToolCallId], 
    does_map_meet_criteria: bool, 
    assessment_reasoning: str, 
    suggested_improvements: Optional[str] = None
) -> Command:
    """Validates the simulated_map_state. Call it when you are sure that the map either meets all criteria, or that it does not"""

    args = extract_tool_args(locals())

    simulated_state = SimulatedGameStateSingleton.get_instance()
    if not suggested_improvements:
        suggested_improvements=""
    if does_map_meet_criteria:
        message = f"Simulated map meets all criteria. Reason: {assessment_reasoning}"

    else:
        message = f"Simulated doesn't meet all criteria. Reason: {assessment_reasoning}. Suggestions: {suggested_improvements}"

    return Command(update={
        logs_field_to_update: [get_log_item("validate_simulated_map", args, False, True, message)],
        messages_field_to_update: [
            ToolMessage(
                get_observation(simulated_state.get_scenario_count(), "validate_simulated_map", True, message),
                tool_call_id=tool_call_id
            )
        ],
        "map_agent_validated": True,
        "map_agent_validation_conclusion_flag": does_map_meet_criteria,
        "map_agent_validation_assessment_reasoning": assessment_reasoning,
        "map_agent_validation_suggested_improvements": suggested_improvements
    })


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