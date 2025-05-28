# manual_tool_test.py
import sys
import os

# Añade la carpeta raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from subsystems.map.schemas.simulated_map import *


def print_step(title: str):
    print(f"\n=== {title.upper()} ===")

if __name__ == "__main__":
    simulated_map = SimulatedMapModel()

    # === CREATE SCENARIOS ===
    print_step("Create Scenarios")
    scenarios = [
        ("Forest Entrance", "Entry point", "Trees", "Start", "outdoor", "forest", "North Woods"),
        ("Deep Forest", "Dense area", "Dark canopy", "Middle", "outdoor", "forest", "North Woods"),
        ("Forest Clearing", "Open space", "Sunny clearing", "Rest area", "outdoor", "clearing", "North Woods"),
        ("Cave Entrance", "Cave mouth", "Stone arch", "Leads underground", "outdoor", "cave", "Mountain Edge"),
        ("Underground Tunnel", "Dark tunnel", "Barely lit path", "Leads deep underground", "indoor", "tunnel", "Mountain Depths")
    ]

    for name, summary, visual, context, inout, typ, zone in scenarios:
        args = CreateScenarioArgs(
            name=name,
            summary_description=summary,
            visual_description=visual,
            narrative_context=context,
            indoor_or_outdoor=inout,
            type=typ,
            zone=zone
        )
        print(simulated_map.create_scenario(args))

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
        print(simulated_map.create_bidirectional_connection(conn_args))

    # === MODIFY A SCENARIO ===
    print_step("Modify Scenario Name")
    modify_args = ModifyScenarioArgs(
        scenario_id="scene_003",
        new_name="Bright Clearing"
    )
    print(simulated_map.modify_scenario(modify_args))

    # === GET SCENARIO DETAILS ===
    print_step("Get Scenario Details")
    details_args = GetScenarioDetailsArgs(scenario_id="scene_004")
    print(simulated_map.get_scenario_details(details_args))

    # === CLUSTER SUMMARY ===
    print_step("List Scenario Clusters")
    summary_args = ListScenariosClusterSummaryArgs(list_all_scenarios_in_each_cluster=True)
    print(simulated_map.list_scenarios_summary_per_cluster(summary_args))

    # === FIND SCENARIOS ===
    print_step("Find Scenarios by Zone")
    find_args = FindScenariosArgs(attribute_to_filter="zone", value_to_match="north woods")
    print(simulated_map.find_scenarios_by_attribute(find_args))

    # === SPATIAL INFO ===
    print_step("SPATIAL INFO")
    spatialinfo_args = GetNeighborsAtDistanceArgs(start_scenario_id="scene_002",max_distance=3)
    print(simulated_map.get_neighbors_at_distance(spatialinfo_args))


    # === FINALIZE ===
    print_step("Finalize Simulation")
    final_args = FinalizeSimulationArgs(justification="Map includes indoor/outdoor areas, multiple connections, and zone variety.")
    final_result = simulated_map.finalize_simulation_and_provide_map(final_args)
    print("Final Justification:", final_result["final_justification"])
    print("Scenarios in Final Map:", len(final_result["final_simulated_map_scenarios"]))
    print("Clusters:", simulated_map.island_clusters)