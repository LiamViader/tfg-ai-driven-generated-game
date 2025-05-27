# manual_tool_test.py

from subsystems.map.agents.tools.map_simulation_tools import SimulatedMapExecutionTools
from subsystems.map.schemas.map_elements import ScenarioModel

# Simulación inicial vacía
initial_scenarios = {}

# Instancia de herramientas
tools = SimulatedMapExecutionTools(initial_scenarios)

# 1. Crear algunos escenarios
print(tools.create_scenario(
    name="Village Entrance",
    narrative_context="You arrive at a small, peaceful village.",
    visual_description="A dusty road leads into a village of stone cottages.",
    summary_description="Entrance to the main village.",
    indoor_or_outdoor="outdoor",
    type="village_entrance",
    zone="Riverland"
))

print(tools.create_scenario(
    name="Blacksmith",
    narrative_context="The local blacksmith works tirelessly.",
    visual_description="An anvil, glowing forge, and racks of weapons.",
    summary_description="A place to craft and repair equipment.",
    indoor_or_outdoor="indoor",
    type="smithy",
    zone="Riverland"
))

# 2. Obtener ID de los escenarios recién creados
scenario_ids = list(tools.simulated_scenarios.keys())
scene1, scene2 = scenario_ids[0], scenario_ids[1]

# 3. Conectar los dos escenarios
print(tools.create_bidirectional_connection(
    from_scenario_id=scene1,
    direction_from_origin="north",
    to_scenario_id=scene2,
    connection_type="path",
    travel_description="A cobblestone path leads to the blacksmith.",
    traversal_conditions=["none"]
))

# 4. Ver detalles del primer escenario
print(tools.get_scenario_details(scenario_id=scene1))

# 5. Consultar salidas libres del primer escenario
print(tools.get_available_exit_directions(scenario_id=scene1))

# 6. Buscar por atributo
print(tools.find_scenarios_by_attribute(
    attribute_to_filter="zone",
    value_to_match="Riverland"
))

# 7. Resumen de clústeres
print(tools.list_scenarios_summary_per_cluster())

# 8. Finalizar simulación
print(tools.finalize_simulation_and_provide_map(
    justification="The basic map includes a key village entry point and blacksmith connected logically."
))
