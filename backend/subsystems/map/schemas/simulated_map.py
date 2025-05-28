from typing import Dict, List, Any, Optional, Literal, Set, Tuple
from pydantic import BaseModel, model_validator, Field as PydanticField
from langchain_core.tools import tool
from copy import deepcopy
from subsystems.map.schemas.descriptions import SCENARIO_FIELDS, EXIT_FIELDS
import re

from subsystems.map.schemas.map_elements import ScenarioModel, Direction, OppositeDirections, ExitInfo


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





class SimulatedMapModel(BaseModel):
    simulated_scenarios: Dict[str, ScenarioModel] = PydanticField(default_factory=dict, description="A dictionary mapping scenario IDs to their corresponding ScenarioModel objects. Represents the current state of all scenarios in the simulated map.")
    applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, including 'tool_called', 'args', 'success', 'message'.")
    island_clusters: List[Set[str]] = PydanticField(default_factory=list, description="A list of clusters (sets of scenario IDs), where each cluster represents a group of interconnected scenarios. Scenarios that are not connected to others form singleton clusters.")
    
    #S'executa just després de validar i crear-se l'instancia
    @model_validator(mode="after")
    def compute_clusters_on_init(self) -> 'SimulatedMapModel':
        self._compute_island_clusters()
        return self

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

    def _compute_island_clusters(self):
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
        self.island_clusters=clusters

    def _format_cluster_summary(self, list_all_scenarios: bool, max_listed_per_cluster: Optional[int] = 5) -> str:
        """
        Generates a formatted string summarizing connectivity clusters.
        Lists all scenarios (ID and name) per cluster if list_all_scenarios is True.
        Otherwise, lists up to 'max_listed_per_cluster' scenarios per cluster.
        """
        if not self.island_clusters:
            return "The simulated map currently has 0 scenarios."
        
        summary = f"The simulated map has {len(self.simulated_scenarios)} scenarios and {len(self.island_clusters)} cluster(s) of scenarios:\n"
        for i, cluster_set in enumerate(self.island_clusters, 1):
            cluster_list_sorted = sorted(list(cluster_set)) 
            
            scenario_strings = []
            num_to_display = len(cluster_list_sorted) if list_all_scenarios else (max_listed_per_cluster or len(cluster_list_sorted))

            for k, scenario_id in enumerate(cluster_list_sorted):
                if k < num_to_display:
                    scenario = self.simulated_scenarios.get(scenario_id)
                    if scenario:
                        scenario_strings.append(f'"{scenario.name}" (ID: {scenario.id})')
                else:
                    break
            
            summary_line = f"- Cluster {i} (contains {len(cluster_list_sorted)} scenarios): "
            if scenario_strings:
                summary_line += ", ".join(scenario_strings)
                if not list_all_scenarios and len(cluster_list_sorted) > num_to_display:
                    summary_line += f", ...and {len(cluster_list_sorted) - num_to_display} more."
            else:
                summary_line += "(No scenarios found for this cluster - this might indicate an issue)."

            summary += summary_line + "\n"
        return summary.strip()

    def _log_and_summarize(self, tool_name: str, args: BaseModel, success: bool, message: str) -> str:
        """Helper to log the operation and create consistent observation messages."""
        self.applied_operations_log.append({
            "tool_called": tool_name,
            "args": args.model_dump(),
            "success": success,
            "message": message
        })
        
        observation = f"Result of '{tool_name}': {message}"
        return observation

    def create_scenario(self, args_model: CreateScenarioArgs) -> str:
        
        """Creates a new scenario in the simulated map."""
        effective_id = self.generate_sequential_scene_id(list(self.simulated_scenarios.keys()))

        try:
            new_scenario_data = {
                "id": effective_id,
                "name": args_model.name,
                "summary_description": args_model.summary_description,
                "visual_description": args_model.visual_description,
                "narrative_context": args_model.narrative_context,
                "indoor_or_outdoor": args_model.indoor_or_outdoor,
                "type": args_model.type,
                "zone": args_model.zone,
                "exits": {}
            }
            new_scenario = ScenarioModel(**new_scenario_data)  # Pydantic validation
            self.simulated_scenarios[effective_id] = new_scenario
            self.island_clusters.append({effective_id})
            return self._log_and_summarize("create_scenario_in_simulation", args_model, True, f"Scenario '{args_model.name}' (ID: {effective_id}) created successfully. Map now has {len(self.simulated_scenarios)} scenarios.")
        except Exception as e:
            return self._log_and_summarize("create_scenario", args_model, False, f"Error while creating scenario: {e}")

    def modify_scenario(self, args_model: ModifyScenarioArgs) -> str:
        """Modifies the specified scenario. Only the provided fields will be updated."""

        if args_model.scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("modify_scenario", args_model, False, f"Scenario with ID '{args_model.scenario_id}' does not exist.")


        # Apply changes only if the fields are not None
        scenario = self.simulated_scenarios[args_model.scenario_id]
        updated_fields = []
        if args_model.new_name is not None: scenario.name = args_model.new_name; updated_fields.append("name")
        if args_model.new_summary_description is not None: scenario.summary_description = args_model.new_summary_description; updated_fields.append("summary_description")
        if args_model.new_visual_description is not None: scenario.visual_description = args_model.new_visual_description; updated_fields.append("visual_description")
        if args_model.new_narrative_context is not None: scenario.narrative_context = args_model.new_narrative_context; updated_fields.append("narrative_context")
        if args_model.new_indoor_or_outdoor is not None: scenario.indoor_or_outdoor = args_model.new_indoor_or_outdoor; updated_fields.append("indoor_or_outdoor")
        if args_model.new_type is not None: scenario.type = args_model.new_type; updated_fields.append("type")
        if args_model.new_zone is not None: scenario.zone = args_model.new_zone; updated_fields.append("zone")

        return self._log_and_summarize("modify_scenario_in_simulation", args_model, True, f"Scenario '{args_model.scenario_id}' modified. Updated fields: {', '.join(updated_fields) if updated_fields else 'None'}.")
    
    def delete_scenario(self, args_model: DeleteScenarioArgs) -> str:
        """Deletes the specified scenario. An scenario should only be deleted if necessary to complete the task"""

        if args_model.scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("delete_scenario", args_model, False, f"Scenario with ID '{args_model.scenario_id}' does not exist.")
        
        for other_id, other_scenario in self.simulated_scenarios.items():
            for direction, exit_info in other_scenario.exits.items():
                if exit_info and exit_info.target_scenario_id == args_model.scenario_id:
                    other_scenario.exits[direction] = None

        # Remove the scenario itself
        del self.simulated_scenarios[args_model.scenario_id]

        # Recompute island clusters
        self._compute_island_clusters()
        
        return self._log_and_summarize("delete_scenario", args_model, True, f"Scenario '{args_model.scenario_id}' deleted successfully.")

    def create_bidirectional_connection(self, args_model: CreateBidirectionalConnectionArgs) -> str:
        """Creates a new bidirectional connection between two existing scenarios in the simulation."""

        if args_model.from_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Origin scenario ID '{args_model.from_scenario_id}' not fpund.")
        if args_model.to_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Destination scenario ID '{args_model.to_scenario_id}' not found.")
        if args_model.from_scenario_id == args_model.to_scenario_id:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, "Error: Cannot connect a scenario to itself.")

        origin_scenario = self.simulated_scenarios[args_model.from_scenario_id]
        destination_scenario = self.simulated_scenarios[args_model.to_scenario_id]
        
        direction_to_origin = OppositeDirections[args_model.direction_from_origin]

        if origin_scenario.exits.get(args_model.direction_from_origin) is not None:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Origin scenario '{args_model.from_scenario_id}' already has an exit to the '{args_model.direction_from_origin}'.")
        if destination_scenario.exits.get(direction_to_origin) is not None:
            return self._log_and_summarize("create_bidirectional_connection", args_model, False, f"Error: Destination scenario '{args_model.to_scenario_id}' already has an exit to its '{direction_to_origin}' (which would be the return path).")

        # Create exits
        exit_info_origin = ExitInfo(
            target_scenario_id=args_model.to_scenario_id,
            connection_type=args_model.connection_type,
            travel_description=args_model.travel_description,
            traversal_conditions=args_model.traversal_conditions or []
        )
        # For the return path, we might want separate descriptions/conditions, or mirror them.
        # For now, mirror connection_type, and conditions. Travel description could be generic.
        exit_info_destination = ExitInfo(
            target_scenario_id=args_model.from_scenario_id,
            connection_type=args_model.connection_type, # Mirrored
            travel_description=args_model.travel_description,
            traversal_conditions=args_model.traversal_conditions or [] # Mirrored
        )

        origin_scenario.exits[args_model.direction_from_origin] = exit_info_origin
        destination_scenario.exits[direction_to_origin] = exit_info_destination
        
        #recompute topology
        self._compute_island_clusters()
        return self._log_and_summarize("create_bidirectional_connection", args_model, True, f"Connection type'{args_model.connection_type}' created: '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) <-> '{args_model.to_scenario_id}' ({direction_to_origin}).")


    def delete_bidirectional_connection(self, args_model: DeleteBidirectionalConnectionArgs) -> str:
        """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""

        if args_model.scenario_id_A not in self.simulated_scenarios:
            return self._log_and_summarize("delete_bidirectional_connection", args_model, False, f"Error: Scenario A ID '{args_model.scenario_id_A}' not found.")
        
        scenario_A = self.simulated_scenarios[args_model.scenario_id_A]
        exit_info_A_to_B = scenario_A.exits.get(args_model.direction_from_A)

        if not exit_info_A_to_B:
            return self._log_and_summarize("delete_bidirectional_connection", args_model, False, f"Error: Scenario '{args_model.scenario_id_A}' has no exit to the '{args_model.direction_from_A}'.")

        scenario_id_B = exit_info_A_to_B.target_scenario_id
        if scenario_id_B not in self.simulated_scenarios:
            # Inconsistent state, but tool should handle it by just clearing A's exit
            scenario_A.exits[args_model.direction_from_A] = None
            self._compute_island_clusters()
            return self._log_and_summarize("delete_bidirectional_connection", args_model, True, f"Exit from '{args_model.scenario_id_A}' ({args_model.direction_from_A}) cleared. Target scenario '{scenario_id_B}' was not found (map was possibly inconsistent).")

        scenario_B = self.simulated_scenarios[scenario_id_B]
        direction_from_B = OppositeDirections[args_model.direction_from_A]

        # Clear both exits
        scenario_A.exits[args_model.direction_from_A] = None
        # Check if the reverse exit actually points back as expected
        exit_B_to_A = scenario_B.exits.get(direction_from_B)
        if exit_B_to_A and exit_B_to_A.target_scenario_id == args_model.scenario_id_A:
            scenario_B.exits[direction_from_B] = None
            message = f"Bidirectional connection '{args_model.scenario_id_A}' ({args_model.direction_from_A}) <-> '{scenario_id_B}' ({direction_from_B}) deleted."
        else:
            message = f"Exit from '{args_model.scenario_id_A}' ({args_model.direction_from_A}) to '{scenario_id_B}' deleted. Reverse connection from '{scenario_id_B}' not found or not pointing back as expected."
            
        self._compute_island_clusters() # Rcompute topology
        return self._log_and_summarize("delete_bidirectional_connection", args_model, True, message)

    def modify_bidirectional_connection(
        self, 
        args_model: ModifyBidirectionalConnectionArgs
    ) -> str:
        """Modifies attributes of an existing bidirectional connection. Only provided attributes are changed."""
        

        if args_model.from_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Error: Origin scenario ID '{args_model.from_scenario_id}' not found.")

        origin_scenario = self.simulated_scenarios[args_model.from_scenario_id]
        exit_info_origin = origin_scenario.exits.get(args_model.direction_from_origin)

        if not exit_info_origin:
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Error: Scenario '{args_model.from_scenario_id}' has no exit to the '{args_model.direction_from_origin}'.")

        to_scenario_id = exit_info_origin.target_scenario_id
        if to_scenario_id not in self.simulated_scenarios:
            # Connection points to a non-existent scenario, data inconsistency.
            return self._log_and_summarize("modify_bidirectional_connection", args_model, False, f"Exit from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) points to target scenario '{to_scenario_id}' not found.")

        destination_scenario = self.simulated_scenarios[to_scenario_id]
        direction_to_origin = OppositeDirections[args_model.direction_from_origin]
        exit_info_destination = destination_scenario.exits.get(direction_to_origin)

        updated_fields_origin = []
        if args_model.new_connection_type is not None: exit_info_origin.connection_type = args_model.new_connection_type; updated_fields_origin.append("connection_type")
        if args_model.new_travel_description is not None: exit_info_origin.travel_description = args_model.new_travel_description; updated_fields_origin.append("travel_description")
        if args_model.new_traversal_conditions is not None: exit_info_origin.traversal_conditions = args_model.new_traversal_conditions; updated_fields_origin.append("traversal_conditions")

        if exit_info_destination and exit_info_destination.target_scenario_id == args_model.from_scenario_id:
            # Modify reverse path symmetrically for type and conditions, travel_description could be different.
            if args_model.new_connection_type is not None: exit_info_destination.connection_type = args_model.new_connection_type
            if args_model.new_traversal_conditions is not None: exit_info_destination.traversal_conditions = args_model.new_traversal_conditions
            if args_model.new_travel_description is not None: exit_info_destination.travel_description = args_model.new_travel_description
            message = f"Bidirectional connection from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) <-> '{to_scenario_id}' ({direction_to_origin}) modified. Updated fields: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
        else:
            message = f"Exit from '{args_model.from_scenario_id}' ({args_model.direction_from_origin}) modified. Reverse connection from '{to_scenario_id}' not found or not pointing back as expected. Updated fields on forward path: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."

        return self._log_and_summarize("modify_bidirectional_connection", args_model, True, message)

    def get_scenario_details(self, args_model: GetScenarioDetailsArgs) -> str:
        """(QUERY tool) Retrieves and returns all details for a specific scenario in the simulated map."""
        if args_model.scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("get_scenario_details", args_model, False, f"Error: Scenario ID '{args_model.scenario_id}' not found.")
        
        scenario = self.simulated_scenarios[args_model.scenario_id]
        details_str = f"Details for Scenario: {scenario.id}:\n"
        details_str += f"  ID: {scenario.id}\n"
        details_str += f"  Name: {scenario.name}\n"
        details_str += f"  Type: {scenario.type}\n"
        details_str += f"  Zone: {scenario.zone}\n"
        details_str += f"  Indoor or outdoor: {scenario.indoor_or_outdoor}\n"
        details_str += f"  Summary Description: {scenario.summary_description}\n"
        details_str += f"  Visual Description: {scenario.visual_description}\n"
        details_str += f"  Narrative Context: {scenario.narrative_context}\n"
        details_str +=  "  Connections:\n"
        if any(exit_info for exit_info in scenario.exits.values()):
            for direction, exit_info in scenario.exits.items():
                if exit_info:
                    details_str += f"    - {direction}: to '{exit_info.target_scenario_id}' (Connection type: {exit_info.connection_type}, Conditions: {exit_info.traversal_conditions}, Travel: \"{exit_info.travel_description}\")\n"
                else:
                    details_str += f"    - {direction}: (None)\n"
        else:
            details_str += "    (No exits defined)\n"
        return self._log_and_summarize("get_scenario_details", args_model, True, details_str)

    def get_neighbors_at_distance(self, args_model:GetNeighborsAtDistanceArgs) -> str:
        """(QUERY tool) Retrieves scenarios within N hops from a starting scenario, including connection details. Use this to understand spatial composition of a zone"""
        if args_model.start_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("get_neighbors_at_distance", args_model, False, f"Error: Start scenario ID '{args_model.start_scenario_id}' not found.")

        output_lines = [f"Neighbors of '{self.simulated_scenarios[args_model.start_scenario_id].name}' (ID: {args_model.start_scenario_id}) up to distance {args_model.max_distance}:"]
        # BFS: (scenario_id, current_distance, path_description_list)
        queue: List[Tuple[str, int, List[str]]] = [(args_model.start_scenario_id, 0, [])]
        # Visited format: {scenario_id: distance_found_at} to find shortest paths
        visited_at_dist: Dict[str, int] = {args_model.start_scenario_id: 0}
        
        results_by_distance: Dict[int, List[str]] = {dist: [] for dist in range(1, args_model.max_distance + 1)}

        head = 0
        while head < len(queue):
            current_id, distance, _ = queue[head] # Path description not used in this version for simplicity of output
            head += 1

            if distance >= args_model.max_distance: continue

            current_scenario = self.simulated_scenarios.get(current_id)
            if not current_scenario or not current_scenario.exits: continue

            for direction, exit_info in current_scenario.exits.items():
                if exit_info and exit_info.target_scenario_id in self.simulated_scenarios:
                    neighbor_id = exit_info.target_scenario_id
                    # Process if not visited, or found via a shorter/equal path to add all connections at this distance
                    if neighbor_id not in visited_at_dist or visited_at_dist[neighbor_id] >= distance + 1 :
                        if neighbor_id not in visited_at_dist : # Add to queue only if truly new or shorter path (for BFS structure)
                            visited_at_dist[neighbor_id] = distance + 1
                            if distance + 1 < args_model.max_distance : # Only add to queue if we need to explore further from it
                                queue.append((neighbor_id, distance + 1, []))
                        
                        if visited_at_dist[neighbor_id] == distance + 1: # ensure we only list it once per distance level from different paths
                            neighbor_scenario = self.simulated_scenarios[neighbor_id]
                            connection_desc = f"from '{current_scenario.name}' (ID: {current_id}) via '{direction}' (exit type: {exit_info.connection_type})"
                            entry_str = f"- '{neighbor_scenario.name}' (ID: {neighbor_id}, Type: {neighbor_scenario.type}, Zone: {neighbor_scenario.zone}) reached {connection_desc}."
                            if entry_str not in results_by_distance[distance + 1]: # Avoid duplicate entries if multiple paths lead at same shortest distance
                                results_by_distance[distance + 1].append(entry_str)
        
        has_results = False
        for dist_level in range(1, args_model.max_distance + 1):
            if results_by_distance[dist_level]:
                has_results = True
                output_lines.append(f"Distance {dist_level}:")
                output_lines.extend(sorted(results_by_distance[dist_level]))
        
        if not has_results:
            output_lines.append("(No new neighbors found within the specified distance via explored paths).")

        return self._log_and_summarize("get_neighbors_at_distance", args_model, True, "\n".join(output_lines))

    def list_scenarios_summary_per_cluster(self, args_model: ListScenariosClusterSummaryArgs) -> str:
        """
        (QUERY tool) Summarizes scenario connectivity clusters in the map. A cluster is a group of interconnected scenarios. Lists scenario IDs and names per cluster, either all or a limited sample. Use this tool to list scenarios.
        """

        if not self.simulated_scenarios:
            return self._log_and_summarize("list_scenarios_summary_per_cluster", args_model, True, "The simulated map is currently empty. No clusters to display.")
        
        summary_text = self._format_cluster_summary(
            list_all_scenarios=args_model.list_all_scenarios_in_each_cluster,
            max_listed_per_cluster=args_model.max_scenarios_to_list_per_cluster_if_not_all
        )
        
        return self._log_and_summarize("list_scenarios_summary_per_cluster", args_model, True, f"Current map connectivity cluster summary:\n{summary_text}")

    def find_scenarios_by_attribute(self, args_model: FindScenariosArgs) -> str:
        """(QUERY tool) Finds scenarios matching a given attribute and value. Case-insensitive for 'name_contains'."""
        matches = []
        value_to_match_lower = args_model.value_to_match.lower()

        for scenario in self.simulated_scenarios.values():
            if len(matches) >= (args_model.max_results or 5): break

            if args_model.attribute_to_filter == "type" and getattr(scenario, 'type', '').lower() == value_to_match_lower:
                matches.append(f'- ID: {scenario.id}, Name: "{scenario.name}", Type: {scenario.type}')
            elif args_model.attribute_to_filter == "indoor_or_outdoor" and getattr(scenario, 'indoor_or_outdoor', '').lower() == value_to_match_lower:
                matches.append(f'- ID: {scenario.id}, Name: "{scenario.name}", {scenario.indoor_or_outdoor}')
            elif args_model.attribute_to_filter == "name_contains" and value_to_match_lower in scenario.name.lower():
                matches.append(f'- ID: {scenario.id}, Name: "{scenario.name}"')
            elif args_model.attribute_to_filter == "zone" and getattr(scenario, 'zone', '').lower() == value_to_match_lower:
                matches.append(f'- ID: {scenario.id}, Name: "{scenario.name}", Zone: "{scenario.zone}"')
        
        if not matches:
            return self._log_and_summarize("find_scenarios_by_attribute", args_model, True, f"No scenarios found matching '{args_model.attribute_to_filter}' with value '{args_model.value_to_match}'.")
        
        return self._log_and_summarize("find_scenarios_by_attribute", args_model, True, f"Scenarios matching '{args_model.attribute_to_filter}' with value '{args_model.value_to_match}':\n" + "\n".join(matches))

    def get_bidirectional_connection_details(self, args_model:GetBidirectionalConnectionDetailsArgs) -> str:
        """
        (QUERY tool) Retrieves details for a specific exit from a given scenario. This includes connection type, travel description, and traversal conditions.
        """

        if args_model.from_scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("get_connection_details", args_model, False, f"Error: Scenario ID '{args_model.from_scenario_id}' not found.")

        scenario = self.simulated_scenarios[args_model.from_scenario_id]
        exit_info = scenario.exits.get(args_model.direction)

        if not exit_info:
            return self._log_and_summarize("get_connection_details", args_model, True, f"Scenario '{args_model.from_scenario_id}' has no exit defined in the direction '{args_model.direction}'.")

        details_str = (
            f"Details for exit from '{args_model.from_scenario_id}' towards '{args_model.direction}':\n"
            f"  - Leads to Scenario ID: {exit_info.target_scenario_id}\n"
            f"  - Connection Type: {exit_info.connection_type}\n"
            f"  - Travel Description: {exit_info.travel_description or 'N/A'}\n"
            f"  - Traversal Conditions: {', '.join(exit_info.traversal_conditions) if exit_info.traversal_conditions else 'None'}"
        )
        return self._log_and_summarize("get_connection_details", args_model, True, details_str)

    def get_available_exit_directions(self, args_model: GetAvailableExitsArgs) -> str:
        """
        (QUERY tool) Lists all cardinal directions from a given scenario that do NOT currently have an exit defined. Useful for finding where new connections can be added from this scenario.
        """
        if args_model.scenario_id not in self.simulated_scenarios:
            return self._log_and_summarize("get_available_exit_directions", args_model, False, f"Error: Scenario ID '{args_model.scenario_id}' not found.")

        scenario = self.simulated_scenarios[args_model.scenario_id]
        available_directions = [
            direction for direction in Direction.__args__ # type: ignore
            if scenario.exits.get(direction) is None
        ]

        if not available_directions:
            message = f"Scenario '{scenario.name}' (ID: {args_model.scenario_id}) has no available (empty) exit directions; all directions are occupied or it has no exit slots."
        else:
            message = f"Available (empty) exit directions for scenario '{scenario.name}' (ID: {args_model.scenario_id}): {', '.join(available_directions)}."

        return self._log_and_summarize("get_available_exit_directions", args_model, True, message)

    def finalize_simulation_and_provide_map(self, args_model: FinalizeSimulationArgs) -> Dict[str, Any]:
        """Call this tool ONLY when the simulated map fulfills the objective and all operations are done."""
        self._compute_island_clusters()
        # Log this specific call type
        self.applied_operations_log.append({
            "tool_called": "finalize_simulation_and_provide_map", "args": args_model.model_dump(),
            "success": True, "message": "Simulation finalized."
        })
        return {
            "final_simulated_map_scenarios": {sid: scenario.model_dump() for sid, scenario in self.simulated_scenarios.items()},
            "final_justification": args_model.justification,
            "applied_operations_log": self.applied_operations_log
        }


