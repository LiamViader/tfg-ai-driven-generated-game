# manual_tool_test.py
import sys
import os

# Añade la carpeta raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from simulated.singleton import SimulatedGameStateSingleton
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

def call(tool, **kwargs):
    common = {
        "messages_field_to_update": "messages",
        "logs_field_to_update": "logs",
        "tool_call_id": "manual",
    }
    return tool.invoke({**common, **kwargs})

if __name__ == "__main__":
    SimulatedGameStateSingleton.reset_instance()
    state = SimulatedGameStateSingleton.get_instance()

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
        print(call(
            create_scenario,
            name=name,
            narrative_context=context,
            visual_description=visual,
            visual_prompt=visual_prompt,
            summary_description=summary,
            indoor_or_outdoor=inout,
            type=typ,
            zone=zone,
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
        print(call(
            create_bidirectional_connection,
            scenario_id_A=from_id,
            direction_from_A=direction,
            scenario_id_B=to_id,
            connection_type=conn_type,
            travel_description=f"A {conn_type} from {from_id} to {to_id}.",
            traversal_conditions=[],
        ))

    # === MODIFY A SCENARIO ===
    print_step("Modify Scenario Name")
    print(call(
        modify_scenario,
        scenario_id="scene_003",
        new_name="Bright Clearing",
    ))

    # === GET SCENARIO DETAILS ===
    print_step("Get Scenario Details")
    print(call(
        get_scenario_details,
        scenario_id="scene_004",
    ))

    # === CLUSTER SUMMARY ===
    print_step("List Scenario Clusters")
    print(call(
        list_scenarios_summary_per_cluster,
        list_all_scenarios_in_each_cluster=True,
    ))

    # === FIND SCENARIOS ===
    print_step("Find Scenarios by Zone")
    print(call(
        find_scenarios_by_attribute,
        attribute_to_filter="zone",
        value_to_match="north woods",
    ))

    print_step("Find Scenarios by Name Contains")
    print(call(
        find_scenarios_by_attribute,
        attribute_to_filter="name_contains",
        value_to_match="Forest",
    ))

    # === SPATIAL INFO ===
    print_step("SPATIAL INFO")
    print(call(
        get_neighbors_at_distance,
        start_scenario_id="scene_002",
        max_distance=3,
    ))


    # === FINALIZE ===
    print_step("Finalize Simulation")
    final_result = call(
        finalize_simulation,
        justification="Map includes indoor/outdoor areas, multiple connections, and zone variety.",
    )
    print("Final Justification:", final_result.update["map_task_finalized_justification"])
    print("Scenarios in Final Map:", state.get_scenario_count())
    print("Clusters:", state.read_only_map.get_cluster_summary(list_all_scenarios_in_each_cluster=True))
