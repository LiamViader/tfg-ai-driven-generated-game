# manual_tool_test.py
import sys
import os

# Añade la carpeta raíz del proyecto a sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from typing import Dict, List, Any, Optional, Literal, Set, Tuple
from pydantic import BaseModel, Field as PydanticField
from langchain_core.tools import tool
from copy import deepcopy
from subsystems.map.schemas.descriptions import SCENARIO_FIELDS, EXIT_FIELDS
import re

from subsystems.map.schemas.map_elements import ScenarioModel, Direction, OppositeDirections, ExitInfo # Asegúrate de importar todo lo necesario
# from ...operations import scenario_ops, connection_ops # Aún los necesitarás para la lógica interna


""""RECORDAR IMPLEMENTAR EINES DE MODIFICACIÓ I DE CONSULTA I A LA DESCRIPCIÓ DEIXAR CLAR SI ES DE CONSULTA O DE MODIFICACIÓ"""


#Schemas Pydantic for args
#Scenario

class CreateScenarioArgs(BaseModel):
    name: str = PydanticField(..., description=SCENARIO_FIELDS["name"])
    summary_description: str = PydanticField(..., description=SCENARIO_FIELDS["summary_description"])
    visual_description: str = PydanticField(..., description=SCENARIO_FIELDS["visual_description"])
    narrative_context: str = PydanticField(..., description=SCENARIO_FIELDS["narrative_context"])
    indoor_or_outdoor: Literal["indoor", "outdoor"] = PydanticField(..., description=SCENARIO_FIELDS["indoor_or_outdoor"])
    type: str = PydanticField(..., description=SCENARIO_FIELDS["type"])
    zone: str = PydanticField(..., description=SCENARIO_FIELDS["zone"])

class ModifyScenarioArgs(BaseModel):
    scenario_id: str = PydanticField(..., description="ID of the scenario to modify.")
    new_name: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["name"])
    new_summary_description: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["summary_description"])
    new_visual_description: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["visual_description"])
    new_narrative_context: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["narrative_context"])
    new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = PydanticField(None, description=SCENARIO_FIELDS["indoor_or_outdoor"])
    new_type: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["type"])
    new_zone: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["zone"])

class DeleteScenarioArgs(BaseModel):
    scenario_id: str = PydanticField(..., description="ID of the scenario to delete.")

#Exits

class CreateBidirectionalConnectionArgs(BaseModel):
    from_scenario_id: str = PydanticField(..., description="ID of the origin scenario.")
    direction_from_origin: Direction = PydanticField(..., description="Direction of the exit from the origin scenario.")
    to_scenario_id: str = PydanticField(..., description="ID of the destination scenario.")
    connection_type: str = PydanticField(..., description=EXIT_FIELDS["connection_type"])
    travel_description: Optional[str] = PydanticField(None, description=EXIT_FIELDS["travel_description"])
    traversal_conditions: List[str] = PydanticField(default_factory=list, description=EXIT_FIELDS["traversal_conditions"]) 

class DeleteBidirectionalConnectionArgs(BaseModel):
    scenario_id_A: str = PydanticField(..., description="ID of the first scenario in the connection.")
    direction_from_A: Direction = PydanticField(..., description="The direction of the exit from scenario_id_A that forms part of the connection to delete.")


class ModifyBidirectionalConnectionArgs(BaseModel): # Schema Refinado
    from_scenario_id: str = PydanticField(..., description="ID of the origin scenario of the connection leg to modify.")
    direction_from_origin: Direction = PydanticField(..., description="Direction of the exit from the origin scenario that identifies the connection leg.")
    new_connection_type: Optional[str] = PydanticField(None, description="New type for the connection.")
    new_travel_description: Optional[str] = PydanticField(None, description="New travel description for the path.")
    new_traversal_conditions: Optional[List[str]] = PydanticField(None, description="New traversal conditions for the connection.")

#Querys

class GetScenarioDetailsArgs(BaseModel):
    scenario_id: str = PydanticField(..., description="ID of the scenario for which to retrieve details.")

class GetNeighborsAtDistanceArgs(BaseModel):
    start_scenario_id: str = PydanticField(..., description="ID of the scenario from which to start the search.")
    max_distance: int = PydanticField(..., description="Maximum distance (number of hops) to explore. Recommended 2-3.", ge=1, le=4)

class ListScenariosClusterSummaryArgs(BaseModel):
    list_all_scenarios_in_each_cluster: bool = PydanticField(
        default=False,  # Default gives a summary
        description="If True, lists all scenarios (ID and name) in each cluster. If False (default), shows a limited preview per cluster."
    )
    max_scenarios_to_list_per_cluster_if_not_all: Optional[int] = PydanticField(
        default=5,
        description="Max number of scenarios to show per cluster when not listing all. Ignored if 'list_all_scenarios_in_each_cluster' is True."
    )

class FindScenariosArgs(BaseModel):
    attribute_to_filter: Literal["type", "zone", "name_contains", "indoor_or_outdoor"] = PydanticField(..., description="Attribute to filter by.")
    value_to_match: str = PydanticField(..., description="Value the attribute should match or contain.")
    max_results: Optional[int] = PydanticField(5, description="Maximum number of matching scenarios to return.")

class GetBidirectionalConnectionDetailsArgs(BaseModel):
    from_scenario_id: str = PydanticField(..., description="ID of the scenario from which the exit originates.")
    direction: Direction = PydanticField(..., description="Direction of the exit whose details are requested.")

class GetAvailableExitsArgs(BaseModel):
    scenario_id: str = PydanticField(..., description="ID of the scenario to check for available exit directions.")

# Finalize

class FinalizeSimulationArgs(BaseModel): # Esta se mantiene igual
    justification: str = PydanticField(..., description="Justificación de por qué el mapa simulado cumple el objetivo final.")

# --- Clase de Herramientas de Simulación con Métodos Específicos ---



@tool(args_schema=ListScenariosClusterSummaryArgs)
def list_scenarios_summary_per_cluster(list_all_scenarios_in_each_cluster: bool = False, max_scenarios_to_list_per_cluster_if_not_all: Optional[int] = 5) -> str:
    """
    (QUERY tool) Summarizes scenario connectivity clusters in the map. A cluster is a group of interconnected scenarios. Lists scenario IDs and names per cluster, either all or a limited sample. Use this tool to list scenarios.
    """
    print("HELLO")
    


if __name__ == "__main__":
    print("🚀 Iniciando Test de SimulatedMapExecutionTools 🚀")

    print(list_scenarios_summary_per_cluster.invoke({
        "list_all_scenarios_in_each_cluster": True
        # "max_scenarios_to_list_per_cluster_if_not_all" usará su valor por defecto
    }))