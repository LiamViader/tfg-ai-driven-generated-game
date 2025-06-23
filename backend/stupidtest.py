from simulated.game_state import SimulatedGameStateSingleton
from subsystems.agents.map_handler.tools.map_tools import get_neighbors_at_distance
simulated_map = SimulatedGameStateSingleton.get_instance().simulated_map

simulated_map.create_scenario("alo","","","","indoor","","")

simulated_map.create_scenario("alo","","","","indoor","","")

simulated_map.create_bidirectional_connection("scenario_001","west","scenario_002","")

print(simulated_map.find_scenario("scenario_001").get_scenario_model())

print(simulated_map.find_scenario("scenario_002").get_scenario_model())

print(simulated_map.get_connection("scenario_001","west").get_connection_model())

print(simulated_map.get_cluster_summary(True))
