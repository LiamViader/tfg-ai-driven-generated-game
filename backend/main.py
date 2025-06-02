from subsystems.map.orchestrator import get_map_graph_app
from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.schemas.simulated_map import *

from utils.visualize_graph import visualize_map_graph


if __name__ == '__main__':
    state = MapGraphState(
        global_narrative_context="Inheritance cycle",
        map_rules_and_constraints=["Every scenario must be connected to at least 1 other scenario.","Some scenarios must be connected to more than 2 other scenarios", "Spatial arrangement should make sense on a narrative and logical aspect, arrangement should be provokefull", "When traveling long or medium narrative distances between 2 scenarios, they should be connected by an intermidiate scenario that works as a path (road, path, valley, etc)"],
        current_objective="Create a map of 8-11. There should only be 1 cluster when finalized. Some scenarios (if posible more than 1) must be connected to more than 2 other scenarios",
        other_guidelines="Make sure that any interior scenarios can be accessed through their corresponding exterior scenario, you can make a fully interior zone if needed. Some connection should have a condition to travel through, lore accurate",
        requesting_agent_id= None,
        max_executor_iterations=15,
        max_validation_iterations=4,
        max_retries=2
    )
    print("--- INVOKE ---")
    map_generation_app=get_map_graph_app()
    final_state = map_generation_app.invoke(state,{"recursion_limit": 200})
    final_map_graph_state_instance = MapGraphState(**final_state)

    print("\n--- FINAL STATE ---\n\n")
    print(final_map_graph_state_instance.working_simulated_map.list_scenarios_summary_per_cluster(ListScenariosClusterSummaryArgs(list_all_scenarios_in_each_cluster=True)))
    print(final_map_graph_state_instance.working_simulated_map.get_neighbors_at_distance(GetNeighborsAtDistanceArgs(start_scenario_id="scene_002",max_distance=4)))

    visualize_map_graph(final_map_graph_state_instance.working_simulated_map)
