from subsystems.map.orchestrator import get_map_graph_app
from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.schemas.simulated_map import *

if __name__ == '__main__':
    state = MapGraphState(
        global_narrative_context="Fantasy tale that occurs in a village of magicians",
        map_rules_and_constraints=["Every scenario must be connected to at least 1 other scenario (Preferable more than 1).", "Spatial arrangement should make sense on a narrative and logical aspect, arrangement should be provokefull"],
        current_objective="Create the map of scenarios 7 scenarios",
        requesting_agent_id= None,
        previous_feedback="",
        max_iterations=20,
    )
    print("--- INVOKE ---")
    map_generation_app=get_map_graph_app()
    final_state = map_generation_app.invoke(state,{"recursion_limit": 100})
    final_map_graph_state_instance = MapGraphState(**final_state)

    print("\n--- FINAL STATE ---\n\n")
    print(final_map_graph_state_instance.working_simulated_map.list_scenarios_summary_per_cluster(ListScenariosClusterSummaryArgs(list_all_scenarios_in_each_cluster=True)))
    print(final_map_graph_state_instance.working_simulated_map.get_neighbors_at_distance(GetNeighborsAtDistanceArgs(start_scenario_id="scene_002",max_distance=4)))

