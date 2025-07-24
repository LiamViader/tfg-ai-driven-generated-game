from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.agents.map_handler.orchestrator import get_map_graph_app
from simulated.singleton import SimulatedGameStateSingleton
from utils import visualize_graph
def run_map_agent_test(initial_state: MapGraphState, title: str):
    print(f"\n=== TEST: {title} ===")
    # Reiniciar estat del món abans de començar
    SimulatedGameStateSingleton.reset_instance()
    app = get_map_graph_app()
    final_state = app.invoke(initial_state, {"recursion_limit": 1000})
    visualize_graph.visualize_map_graph()

if __name__ == "__main__":
    # 🔹 OBJECTIU 1: Crear dues regions amb 3 escenaris cadascuna
    objective_1 = "Create a map with two regions: the Sunken Dunes and the Temple Peaks. Each should contain 3 unique scenarios, with clear connections."
    constraints = [
        "All scenarios must be connected to at least one other.",
        "Each region must contain at least 2 locations.",
        "Transitions between zones must be explained (e.g., tunnel, gate)."
    ]


    # 🔹 OBJECTIU 2: Hub central + 4 ubicacions amb condicions d’accés
    objective_2 = "Design a central hub surrounded by 4 outer locations, each of those should be surrounded by 1 other."
    constraints_obj2 = [
        "Every outer location must not connect to any other except the central hub.",
        "All paths must include a described access condition (e.g., 'Only during eclipse')."
    ]

    # Configuracions diferents per l’objectiu 2
    configs_obj2 = [
        ("Conf. 3: execució agressiva sense validació", 14, 0, 0),
    ]

    for title, max_exec, max_val, retries in configs_obj2:
        initial_state = MapGraphState(
            map_foundational_lore_document="This is a jungle planet ruled by ancient tech cults and guarded by mystical access rites.",
            map_rules_and_constraints=constraints_obj2,
            map_current_objective=objective_2,
            map_other_guidelines="Center must be visually distinct and functionally dominant.",
            map_max_executor_iterations=max_exec,
            map_max_validation_iterations=max_val,
            map_max_retries=retries
        )
        run_map_agent_test(initial_state, f"[2] {title}")