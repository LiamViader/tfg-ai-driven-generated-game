from typing import Dict, List, Any, Optional, Literal, Set, Tuple
from pydantic import BaseModel, model_validator, Field as PydanticField
from core_game.map.field_descriptions import SCENARIO_FIELDS, EXIT_FIELDS
import re

from core_game.map.schemas import ScenarioModel, Direction, OppositeDirections, ExitInfo


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
        description="If true, lists all scenarios (ID and name) in each cluster. If false (default), shows a limited preview per cluster. Use true only in limited justified ocasions"
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

class FinalizeSimulationArgs(BaseModel): 
    justification: str = PydanticField(..., description="Justification of why the simulated map meets all criteria.")

# Validate
class ValidateSimulationMapArgs(BaseModel):
    does_map_meet_criteria: bool = PydanticField(..., description="Your assessment: set to True if you believe the map successfully meets all current objectives and constraints; False otherwise.")
    assessment_reasoning: str = PydanticField(..., description="Your concise justification explaining why the map meets (or fails to meet) the objectives and constraints.")
    suggested_improvements: Optional[str] = PydanticField(default=None, description="If `does_map_meet_criteria` is False, provide specific, actionable suggestions on how the map can be modified or updated to meet the unmet criteria. If True, this field can be omitted.")


class SimulatedMapModel(BaseModel):
    simulated_scenarios: Dict[str, ScenarioModel] = PydanticField(default_factory=dict, description="A dictionary mapping scenario IDs to their corresponding ScenarioModel objects. Represents the current state of all scenarios in the simulated map.")
    island_clusters: List[Set[str]] = PydanticField(default_factory=list, description="A list of clusters (sets of scenario IDs), where each cluster represents a group of interconnected scenarios. Scenarios that are not connected to others form singleton clusters.")
    deleted_scenarios: Dict[str, ScenarioModel] = PydanticField(default_factory=dict, description="A dictionary mapping scenario IDs to their corresponding ScenarioModel objects. Stores the scenarios that were deleted.")
    executor_applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, by the executor agent including 'tool_called', 'args', 'success', 'message'.")
    validator_applied_operations_log: List[Dict[str, Any]] = PydanticField(default_factory=list, description="A chronological log of all tool-based operations applied to the simulated map, by the validator agent including 'tool_called', 'args', 'success', 'message'.")
    executor_or_validator: Literal["executor", "validator"] = PydanticField(default="executor", description="Whether the map is currently being used by the executor agent or the validator agent.")

    task_finalized_by_agent: bool = PydanticField(default=False,description="A flag indicating whether the task was finalized by the agent")
    task_finalized_justification: Optional[str] = PydanticField(default=None,description="A string of the justification provided by the agent who finalized the map")

    agent_validation_conclusion_flag: bool = PydanticField(default=False,description="A flag indicating whether the validation agent said the map met all criteria")
    agent_validation_assessment_reasoning: str = PydanticField(default="", description="Reasoning from agent of why the validation he gave.")
    agent_validation_suggested_improvements: str = PydanticField(default="", description="Suggested improvements if the validation agent said map didnt meet criteria.")
    agent_validated: bool = PydanticField(default=False,description="A flag indicating whether the validation agent gave a validation yet")

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
        if self.executor_or_validator == "executor":
            self.executor_applied_operations_log.append({
                "tool_called": tool_name,
                "args": args.model_dump(),
                "success": success,
                "message": message
            })
        else:
            self.validator_applied_operations_log.append({
                "tool_called": tool_name,
                "args": args.model_dump(),
                "success": success,
                "message": message
            })
        
        observation = f"Result of '{tool_name}': {message} \nMap has {len(self.simulated_scenarios)} scenarios."
        print(observation)
        return observation

    def get_summary_list(self)->str:
        return self._format_cluster_summary(list_all_scenarios=False,max_listed_per_cluster=2)


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
            output_lines.append("(No neighbors found within this specified distance via explored paths).")

        return self._log_and_summarize("get_neighbors_at_distance", args_model, True, "\n".join(output_lines))

    def list_scenarios_summary_per_cluster(self, args_model: ListScenariosClusterSummaryArgs) -> str:
        """
        (QUERY tool) Summarizes scenario connectivity clusters in the map. A cluster is a group of interconnected scenarios. Lists scenario IDs and names per cluster, either all or a limited sample. Use this tool to list scenarios. Use this tool to know which scenarios are in diferent clusters.
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


