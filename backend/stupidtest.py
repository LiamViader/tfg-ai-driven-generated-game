from simulated.game_state import SimulatedGameStateSingleton
from subsystems.agents.map_handler.tools.map_tools import get_neighbors_at_distance
simulated_map = SimulatedGameStateSingleton.get_instance().simulated_map

simulated_map.create_scenario("alo","","","","indoor","","")

simulated_map.create_scenario("alo","","","","indoor","","")

simulated_map.create_bidirectional_connection("scenario_001","east","scenario_002","")

print(simulated_map.get_cluster_summary(True))

print(
    get_neighbors_at_distance.invoke(
        {
            "start_scenario_id": "scenario_001",
            "max_distance": 1,
            "tool_call_id": "A"
        }
    )
)