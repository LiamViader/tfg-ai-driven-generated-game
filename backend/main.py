from subsystems.agents.map_handler.orchestrator import get_map_graph_app
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState


from simulated.game_state import SimulatedGameStateSingleton

if __name__ == '__main__':
    state = MapGraphState(
        map_global_narrative_context="A small village of wizzards",
        map_rules_and_constraints=["Every scenario must be connected to at least 1 other scenario.","Some scenarios must be connected to more than 2 other scenarios", "Spatial arrangement should make sense on a narrative and logical aspect, arrangement should be provokefull", "When traveling long or medium narrative distances between 2 scenarios, they should be connected by an intermidiate scenario that works as a path (road, path, valley, etc)"],
        map_current_objective="Create a map of 5-7 scenarios. There should only be 1 cluster when finalized. Some scenarios (if posible more than 1) must be connected to more than 2 other scenarios",
        map_other_guidelines="Make sure that any interior scenarios can be accessed through their corresponding exterior scenario, you can make a fully interior zone if needed. Some connection should have a condition to travel through, lore accurate",
        map_max_executor_iterations=7,
        map_max_validation_iterations=2,
        map_max_retries=3
    )
    print("--- INVOKE ---")
    map_generation_app=get_map_graph_app()
    final_state = map_generation_app.invoke(state,{"recursion_limit": 200})
    final_map_graph_state_instance = MapGraphState(**final_state)

    simulated_map = SimulatedGameStateSingleton.get_instance().simulated_map

    print("\n--- FINAL STATE ---\n\n")
    print(simulated_map.get_cluster_summary(True))

