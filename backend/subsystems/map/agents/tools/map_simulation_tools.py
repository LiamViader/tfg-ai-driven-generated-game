from typing import Dict, List, Any, Optional, Literal, Set
from pydantic import BaseModel, Field as PydanticField
from langchain_core.tools import tool
from copy import deepcopy
from subsystems.map.schemas.descriptions import SCENARIO_FIELDS, EXIT_FIELDS
import re

from ...schemas.map_elements import ScenarioModel, Direction, OppositeDirections, ExitInfo # Asegúrate de importar todo lo necesario
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

class ModifyScenarioArgs(BaseModel):
    scenario_id: str = PydanticField(..., description="ID of the scenario to modify.")
    new_name: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["name"])
    new_summary_description: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["summary_description"])
    new_visual_description: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["visual_description"])
    new_narrative_context: Optional[str] = PydanticField(None, description=SCENARIO_FIELDS["narrative_context"])
    new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = PydanticField(None, description=SCENARIO_FIELDS["indoor_or_outdoor"])

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



# (Define más Schemas para otras herramientas como DeleteScenarioArgs, DeleteConnectionArgs, etc.)

class FinalizeSimulationArgs(BaseModel): # Esta se mantiene igual
    justification: str = PydanticField(..., description="Justificación de por qué el mapa simulado cumple el objetivo final.")

# --- Clase de Herramientas de Simulación con Métodos Específicos ---

class SimulatedMapExecutionTools:
    def __init__(self, initial_scenarios: Dict[str, ScenarioModel]):
        self.simulated_scenarios: Dict[str, ScenarioModel] = deepcopy(initial_scenarios)
        self.applied_operations_log: List[Dict[str, Any]] = []
        self.island_clusters: List[Set[str]] = self._compute_island_clusters()

    @staticmethod
    def generate_sequential_scene_id(existing_ids: List[str]) -> str:
        """Generates a unique ID in the format 'scene_001', 'scene_002', ... based on existing IDs."""
        used_numbers = set()

        pattern = re.compile(r"^scene_(\d+)$")
        for existing_id in existing_ids:
            match = pattern.match(existing_id)
            if match:
                used_numbers.add(int(match.group(1)))

        next_number = 1
        while next_number in used_numbers:
            next_number += 1

        return f"scene_{next_number:03d}"

    def _compute_island_clusters(self) -> List[Set[str]]:
        "Computes the clusters formed by scenarios in the map"
        visited = set()
        clusters = []

        for scenario_id in self.simulated_scenarios:
            if scenario_id not in visited:
                cluster = set()
                to_visit = [scenario_id]
                while to_visit:
                    current = to_visit.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.add(current)
                        exits = self.simulated_scenarios[current].exits
                        connected_ids = [
                            exit_info.target_scenario_id
                            for exit_info in exits.values()
                            if exit_info and exit_info.target_scenario_id in self.simulated_scenarios
                        ]
                        to_visit.extend([sid for sid in connected_ids if sid not in visited])
                clusters.append(cluster)

        return clusters

    def _format_cluster_summary(self) -> str:
        summary = f"The map has {len(self.island_clusters)} clusters:\n"
        for i, cluster in enumerate(self.island_clusters, 1):
            scenario_list = []
            for scenario_id in sorted(cluster):
                scenario = self.simulated_scenarios.get(scenario_id)
                if scenario:
                    scenario_list.append(f'"id": {scenario_id}, "name": {scenario.name}')
            summary += f"- Cluster {i}: {', '.join(scenario_list)}\n"
        return summary.strip()

    def _log_and_summarize(self, tool_name: str, args: BaseModel, success: bool, message: str) -> str:
        """Helper to log the operation and create consistent observation messages."""
        self.applied_operations_log.append({
            "tool_called": tool_name,
            "args": args.model_dump(),
            "success": success,
            "message": message
        })
        
        observation = f"Result of '{tool_name}': {message}. "
        return observation

    @tool(args_schema=CreateScenarioArgs)
    def create_scenario(
        self, 
        name: str, 
        narrative_context: str, 
        visual_description: str, 
        summary_description: str, 
        indoor_or_outdoor: Literal["indoor", "outdoor"]
    ) -> str:
        
        """Creates a new scenario in the simulated map."""
        effective_id = self.generate_sequential_scene_id(list(self.simulated_scenarios.keys()))
        args_model = CreateScenarioArgs(
            name=name,
            summary_description=summary_description,
            visual_description=visual_description,
            narrative_context=narrative_context,
            indoor_or_outdoor=indoor_or_outdoor
        )

        try:
            new_scenario_data = {
                "id": effective_id,
                "name": name,
                "summary_description": summary_description,
                "visual_description": visual_description,
                "narrative_context": narrative_context,
                "indoor_or_outdoor": indoor_or_outdoor,
                "exits": {}
            }
            new_scenario = ScenarioModel(**new_scenario_data)  # Pydantic validation
            self.simulated_scenarios[effective_id] = new_scenario
            self.island_clusters.append({effective_id})
            return self._log_and_summarize("create_scenario", args_model, True, f"Scenario '{name}' (ID: {effective_id}) created successfully.")
        except Exception as e:
            return self._log_and_summarize("create_scenario", args_model, False, f"Error while creating scenario: {e}")

    @tool(args_schema=ModifyScenarioArgs)
    def modify_scenario(
        self,
        scenario_id: str,
        new_name: Optional[str] = None,
        new_summary_description: Optional[str] = None,
        new_visual_description: Optional[str] = None,
        new_narrative_context: Optional[str] = None,
        new_indoor_or_outdoor: Optional[Literal["indoor", "outdoor"]] = None
    ) -> str:
        """Modifies the specified scenario. Only the provided fields will be updated."""
        args_model = ModifyScenarioArgs(
            scenario_id=scenario_id,
            new_name=new_name,
            new_summary_description=new_summary_description,
            new_visual_description=new_visual_description,
            new_narrative_context=new_narrative_context,
            new_indoor_or_outdoor=new_indoor_or_outdoor
        )

        if scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("modify_scenario", args_model, False, f"Scenario with ID '{scenario_id}' does not exist.")

        scenario = self.simulated_scenarios[scenario_id]

        # Apply changes only if the fields are not None
        if new_name is not None:
            scenario.name = new_name
        if new_summary_description is not None:
            scenario.summary_description = new_summary_description
        if new_visual_description is not None:
            scenario.visual_description = new_visual_description
        if new_narrative_context is not None:
            scenario.narrative_context = new_narrative_context
        if new_indoor_or_outdoor is not None:
            scenario.indoor_or_outdoor = new_indoor_or_outdoor

        return self._log_and_summarize("modify_scenario", args_model, True, f"Scenario '{scenario_id}' successfully modified.")
    
    @tool(args_schema=DeleteScenarioArgs)
    def delete_scenario(
        self,
        scenario_id: str
    ) -> str:
        """Deletes the specified scenario. An scenario should only be deleted if necessary to complete the task"""
        args_model = DeleteScenarioArgs(
            scenario_id=scenario_id,
        )
        if scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("delete_scenario", args_model, False, f"Scenario with ID '{scenario_id}' does not exist.")
        
        for other_id, other_scenario in self.simulated_scenarios.items():
            for direction, exit_info in other_scenario.exits.items():
                if exit_info and exit_info.target_scenario_id == scenario_id:
                    other_scenario.exits[direction] = None

        # Remove the scenario itself
        del self.simulated_scenarios[scenario_id]

        # Recompute island clusters
        self.island_clusters = self._compute_island_clusters()
        
        return self._log_and_summarize("delete_scenario", args_model, True, f"Scenario '{scenario_id}' deleted successfully.")

    @tool(args_schema=CreateBidirectionalConnectionArgs)
    def create_bidirectional_connection(
        self, 
        from_scenario_id: str, 
        direction_from_origin: Direction, 
        to_scenario_id: str, 
        connection_type: str, 
        travel_description: Optional[str] = None, 
        traversal_conditions: Optional[List[str]] = None
    ) -> str:
        """Creates a new bidirectional connection between two existing scenarios in the simulation."""

        args_model = CreateBidirectionalConnectionArgs(
            from_scenario_id=from_scenario_id, 
            direction_from_origin=direction_from_origin,
            to_scenario_id=to_scenario_id, 
            connection_type=connection_type,
            travel_description=travel_description, 
            traversal_conditions=traversal_conditions or []
        )

        if from_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Origin scenario ID '{from_scenario_id}' not fpund.")
        if to_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Destination scenario ID '{to_scenario_id}' not found.")
        if from_scenario_id == to_scenario_id:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, "Error: Cannot connect a scenario to itself.")

        origin_scenario = self.simulated_scenarios[from_scenario_id]
        destination_scenario = self.simulated_scenarios[to_scenario_id]
        
        direction_to_origin = OppositeDirections[direction_from_origin]

        if origin_scenario.exits.get(direction_from_origin) is not None:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Origin scenario '{from_scenario_id}' already has an exit to the '{direction_from_origin}'.")
        if destination_scenario.exits.get(direction_to_origin) is not None:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Destination scenario '{to_scenario_id}' already has an exit to its '{direction_to_origin}' (which would be the return path).")

        # Create exits
        exit_info_origin = ExitInfo(
            target_scenario_id=to_scenario_id,
            connection_type=connection_type,
            travel_description=travel_description,
            traversal_conditions=traversal_conditions or []
        )
        # For the return path, we might want separate descriptions/conditions, or mirror them.
        # For now, mirror connection_type, and conditions. Travel description could be generic.
        exit_info_destination = ExitInfo(
            target_scenario_id=from_scenario_id,
            connection_type=connection_type, # Mirrored
            travel_description=travel_description,
            traversal_conditions=traversal_conditions or [] # Mirrored
        )

        origin_scenario.exits[direction_from_origin] = exit_info_origin
        destination_scenario.exits[direction_to_origin] = exit_info_destination
        
        #recompute topology
        self._compute_island_clusters()
        return self._log_and_summarize("create_bidirectional_connection", args_model, True, f"Connection '{connection_type}' created: '{from_scenario_id}' ({direction_from_origin}) <-> '{to_scenario_id}' ({direction_to_origin}).")


    @tool(args_schema=DeleteBidirectionalConnectionArgs)
    def delete_bidirectional_connection(self, scenario_id_A: str, direction_from_A: Direction) -> str:
        """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""
        args_model = DeleteBidirectionalConnectionArgs(scenario_id_A=scenario_id_A, direction_from_A=direction_from_A)

        if scenario_id_A not in self.simulated_scenarios:
            return self._log_and_summarize("delete_bidirectional_connection", args_model, False, f"Error: Scenario A ID '{scenario_id_A}' not found.")
        
        scenario_A = self.simulated_scenarios[scenario_id_A]
        exit_info_A_to_B = scenario_A.exits.get(direction_from_A)

        if not exit_info_A_to_B:
            return self._log_and_summarize("delete_bidirectional_connection", args_model, False, f"Error: Scenario '{scenario_id_A}' has no exit to the '{direction_from_A}'.")

        scenario_id_B = exit_info_A_to_B.target_scenario_id
        if scenario_id_B not in self.simulated_scenarios:
            # Inconsistent state, but tool should handle it by just clearing A's exit
            scenario_A.exits[direction_from_A] = None
            self._compute_island_clusters()
            return self._log_and_summarize("delete_bidirectional_connection", args_model, True, f"Exit from '{scenario_id_A}' ({direction_from_A}) cleared. Target scenario '{scenario_id_B}' was not found (map was possibly inconsistent).")

        scenario_B = self.simulated_scenarios[scenario_id_B]
        direction_from_B = OppositeDirections[direction_from_A]

        # Clear both exits
        scenario_A.exits[direction_from_A] = None
        # Check if the reverse exit actually points back as expected
        exit_B_to_A = scenario_B.exits.get(direction_from_B)
        if exit_B_to_A and exit_B_to_A.target_scenario_id == scenario_id_A:
            scenario_B.exits[direction_from_B] = None
            message = f"Bidirectional connection '{scenario_id_A}' ({direction_from_A}) <-> '{scenario_id_B}' ({direction_from_B}) deleted."
        else:
            message = f"Exit from '{scenario_id_A}' ({direction_from_A}) to '{scenario_id_B}' deleted. Reverse connection from '{scenario_id_B}' not found or not pointing back as expected."
            
        self._compute_island_clusters() # Rcompute topology
        return self._log_and_summarize("delete_bidirectional_connection", args_model, True, message)

    @tool(args_schema=ModifyBidirectionalConnectionArgs)
    def modify_bidirectional_connection(
        self, 
        from_scenario_id: str, 
        direction_from_origin: Direction,
        new_connection_type: Optional[str] = None,
        new_travel_description: Optional[str] = None,
        new_traversal_conditions: Optional[List[str]] = None
    ) -> str:
        """Modifies attributes of an existing bidirectional connection. Only provided attributes are changed."""
        
        args_model = ModifyBidirectionalConnectionArgs(
            from_scenario_id=from_scenario_id, 
            direction_from_origin=direction_from_origin,
            new_connection_type=new_connection_type, 
            new_travel_description=new_travel_description,
            new_traversal_conditions=new_traversal_conditions
        )

        if from_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Error: Origin scenario ID '{from_scenario_id}' not found.")

        origin_scenario = self.simulated_scenarios[from_scenario_id]
        exit_info_origin = origin_scenario.exits.get(direction_from_origin)

        if not exit_info_origin:
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Error: Scenario '{from_scenario_id}' has no exit to the '{direction_from_origin}'.")

        to_scenario_id = exit_info_origin.target_scenario_id
        if to_scenario_id not in self.simulated_scenarios:
            # Connection points to a non-existent scenario, data inconsistency.
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Exit from '{from_scenario_id}' ({direction_from_origin}) points to target scenario '{to_scenario_id}' not found.")

        destination_scenario = self.simulated_scenarios[to_scenario_id]
        direction_to_origin = OppositeDirections[direction_from_origin]
        exit_info_destination = destination_scenario.exits.get(direction_to_origin)

        updated_fields_origin = []
        if new_connection_type is not None: exit_info_origin.connection_type = new_connection_type; updated_fields_origin.append("connection_type")
        if new_travel_description is not None: exit_info_origin.travel_description = new_travel_description; updated_fields_origin.append("travel_description")
        if new_traversal_conditions is not None: exit_info_origin.traversal_conditions = new_traversal_conditions; updated_fields_origin.append("traversal_conditions")

        if exit_info_destination and exit_info_destination.target_scenario_id == from_scenario_id:
            # Modify reverse path symmetrically for type and conditions, travel_description could be different.
            if new_connection_type is not None: exit_info_destination.connection_type = new_connection_type
            if new_traversal_conditions is not None: exit_info_destination.traversal_conditions = new_traversal_conditions
            if new_travel_description is not None: exit_info_destination.travel_description = new_travel_description
            message = f"Bidirectional connection from '{from_scenario_id}' ({direction_from_origin}) <-> '{to_scenario_id}' ({direction_to_origin}) modified. Updated fields: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
        else:
            message = f"Exit from '{from_scenario_id}' ({direction_from_origin}) modified. Reverse connection from '{to_scenario_id}' not found or not pointing back as expected. Updated fields on forward path: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."

        return self._log_and_summarize("modify_bidirectional_connection", args_model, True, message)


    # --- Aquí añadirías más herramientas específicas: ---
    # @tool(args_schema=ModifyScenarioArgs)
    # def modify_scenario_in_simulation(self, scenario_id: str, ...) -> str: ...
    #
    # @tool(args_schema=DeleteScenarioArgs)
    # def delete_scenario_in_simulation(self, scenario_id: str) -> str: ...
    #   (Esta sería compleja, necesitaría limpiar conexiones en otros escenarios)
    #
    # @tool(args_schema=DeleteConnectionArgs)
    # def delete_bidirectional_connection_in_simulation(self, scenario_id: str, direction: Direction) -> str: ...

    @tool(args_schema=FinalizeSimulationArgs)
    def finalize_simulation_and_provide_map(self, justification: str) -> Dict[str, Any]:
        """Llama a esta herramienta ÚNICAMENTE cuando el mapa simulado cumple el objetivo."""
        # ... (igual que antes)
        return {
            "final_simulated_map_scenarios": {sid: scenario.model_dump() for sid, scenario in self.simulated_scenarios.items()},
            "final_justification": justification,
            "applied_operations_log": self.applied_operations_log
        }

    def get_tools(self) -> list:
        return [
            self.create_scenario,
            self.modify_scenario,
            self.delete_scenario,
            self.create_bidirectional_connection,
            self.modify_bidirectional_connection,
            self.delete_bidirectional_connection,
            self.finalize_simulation_and_provide_map
        ]