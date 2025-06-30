# manual_tool_test.py
import sys
import os

# Añade la carpeta raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from subsystems.agents.map_handler.schemas.simulated_map import *
from subsystems.agents.map_handler.tools.map_tools import (
    create_scenario,
    create_bidirectional_connection,
    modify_scenario,
    get_scenario_details,
    list_scenarios_summary_per_cluster,
    find_scenarios_by_attribute,
    get_neighbors_at_distance,
    finalize_simulation,
)


def print_step(title: str):
    print(f"\n=== {title.upper()} ===")

if __name__ == "__main__":
    simulated_map = SimulatedMapModel()

    # === CREATE SCENARIOS ===
    print_step("Create Scenarios")
    scenarios = [
        ("Forest Entrance", "Entry point", "Trees", "Dirt path leading into towering trees", "Start", "outdoor", "forest", "North Woods"),
        ("Deep Forest", "Dense area", "Dark canopy", "Thick foliage with shafts of light", "Middle", "outdoor", "forest", "North Woods"),
        ("Forest Clearing", "Open space", "Sunny clearing", "Grassy patch surrounded by pines", "Rest area", "outdoor", "clearing", "North Woods"),
        ("Cave Entrance", "Cave mouth", "Stone arch", "Jagged rocks framing a shadowed opening", "Leads underground", "outdoor", "cave", "Mountain Edge"),
        ("Underground Tunnel", "Dark tunnel", "Barely lit path", "Rough-hewn walls with dripping water", "Leads deep underground", "indoor", "tunnel", "Mountain Depths")
    ]

    for name, summary, visual_prompt, visual, context, inout, typ, zone in scenarios:
        args = CreateScenarioArgs(
            name=name,
            summary_description=summary,
            visual_prompt=visual_prompt,
            visual_description=visual,
            narrative_context=context,
            indoor_or_outdoor=inout,
            type=typ,
            zone=zone
        )
        print(create_scenario(
            name=args.name,
            narrative_context=args.narrative_context,
            visual_description=args.visual_description,
            visual_prompt=args.visual_prompt,
            summary_description=args.summary_description,
            indoor_or_outdoor=args.indoor_or_outdoor,
            type=args.type,
            zone=args.zone,
            simulated_map_state=simulated_map,
        ))

    # === CONNECT SCENARIOS ===
    print_step("Connect Scenarios")
    connections = [
        ("scene_001", "north", "scene_002", "path"),
        ("scene_002", "east", "scene_003", "trail"),
        ("scene_003", "south", "scene_004", "rocky path"),
        ("scene_004", "south", "scene_005", "ladder")
    ]

    for from_id, direction, to_id, conn_type in connections:
        conn_args = CreateBidirectionalConnectionArgs(
            from_scenario_id=from_id,
            direction_from_origin=direction,
            to_scenario_id=to_id,
            connection_type=conn_type,
            travel_description=f"A {conn_type} from {from_id} to {to_id}.",
            traversal_conditions=[]
        )
        print(create_bidirectional_connection(
            from_scenario_id=conn_args.from_scenario_id,
            direction_from_origin=conn_args.direction_from_origin,
            to_scenario_id=conn_args.to_scenario_id,
            connection_type=conn_args.connection_type,
            travel_description=conn_args.travel_description,
            traversal_conditions=conn_args.traversal_conditions,
            simulated_map_state=simulated_map,
        ))

    # === MODIFY A SCENARIO ===
    print_step("Modify Scenario Name")
    modify_args = ModifyScenarioArgs(
        scenario_id="scene_003",
        new_name="Bright Clearing"
    )
    print(modify_scenario(
        scenario_id=modify_args.scenario_id,
        new_name=modify_args.new_name,
        new_summary_description=None,
        new_visual_description=None,
        new_narrative_context=None,
        new_indoor_or_outdoor=None,
        new_type=None,
        new_zone=None,
        simulated_map_state=simulated_map,
    ))

    # === GET SCENARIO DETAILS ===
    print_step("Get Scenario Details")
    details_args = GetScenarioDetailsArgs(scenario_id="scene_004")
    print(get_scenario_details(
        scenario_id=details_args.scenario_id,
        simulated_map_state=simulated_map,
    ))

    # === CLUSTER SUMMARY ===
    print_step("List Scenario Clusters")
    summary_args = ListScenariosClusterSummaryArgs(list_all_scenarios_in_each_cluster=True)
    print(list_scenarios_summary_per_cluster(
        list_all_scenarios_in_each_cluster=summary_args.list_all_scenarios_in_each_cluster,
        max_scenarios_to_list_per_cluster_if_not_all=summary_args.max_scenarios_to_list_per_cluster_if_not_all,
        simulated_map_state=simulated_map,
    ))

    # === FIND SCENARIOS ===
    print_step("Find Scenarios by Zone")
    find_args = FindScenariosArgs(attribute_to_filter="zone", value_to_match="north woods")
    print(find_scenarios_by_attribute(
        attribute_to_filter=find_args.attribute_to_filter,
        value_to_match=find_args.value_to_match,
        max_results=find_args.max_results,
        simulated_map_state=simulated_map,
    ))

    # === SPATIAL INFO ===
    print_step("SPATIAL INFO")
    spatialinfo_args = GetNeighborsAtDistanceArgs(start_scenario_id="scene_002",max_distance=3)
    print(get_neighbors_at_distance(
        start_scenario_id=spatialinfo_args.start_scenario_id,
        max_distance=spatialinfo_args.max_distance,
        simulated_map_state=simulated_map,
    ))


    # === FINALIZE ===
    print_step("Finalize Simulation")
    final_args = FinalizeSimulationArgs(justification="Map includes indoor/outdoor areas, multiple connections, and zone variety.")
    final_result = finalize_simulation(
        justification=final_args.justification,
        simulated_map_state=simulated_map,
    )
    print("Final Justification:", final_result["final_justification"])
    print("Scenarios in Final Map:", len(final_result["final_simulated_map_scenarios"]))
    print("Clusters:", simulated_map.island_clusters)