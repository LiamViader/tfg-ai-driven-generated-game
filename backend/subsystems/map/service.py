from typing import Optional
from core_game.map.schemas import ScenarioModel, OppositeDirections, ExitInfo
from subsystems.map.schemas.simulated_map import (
    SimulatedMapModel,
    CreateScenarioArgs,
    ModifyScenarioArgs,
    DeleteScenarioArgs,
    CreateBidirectionalConnectionArgs,
    DeleteBidirectionalConnectionArgs,
    ModifyBidirectionalConnectionArgs,
    FinalizeSimulationArgs,
    ValidateSimulationMapArgs,
)


class MapService:
    """Service layer that encapsulates operations on :class:`SimulatedMapModel`."""

    def __init__(self, map_model: Optional[SimulatedMapModel] = None):
        self.map: SimulatedMapModel = map_model or SimulatedMapModel()

    def create_scenario(self, args: CreateScenarioArgs) -> str:
        """Creates a new scenario in the simulated map."""
        effective_id = self.map.generate_sequential_scene_id(list(self.map.simulated_scenarios.keys()))

        try:
            new_scenario_data = {
                "id": effective_id,
                "name": args.name,
                "summary_description": args.summary_description,
                "visual_description": args.visual_description,
                "narrative_context": args.narrative_context,
                "indoor_or_outdoor": args.indoor_or_outdoor,
                "type": args.type,
                "zone": args.zone,
                "exits": {},
            }
            new_scenario = ScenarioModel(**new_scenario_data)
            self.map.simulated_scenarios[effective_id] = new_scenario
            self.map.island_clusters.append({effective_id})
            return self.map._log_and_summarize(
                "create_scenario_in_simulation",
                args,
                True,
                f"Scenario '{args.name}' (ID: {effective_id}) created successfully.",
            )
        except Exception as e:
            return self.map._log_and_summarize(
                "create_scenario",
                args,
                False,
                f"Error while creating scenario: {e}",
            )

    def modify_scenario(self, args: ModifyScenarioArgs) -> str:
        """Modifies the specified scenario. Only the provided fields will be updated."""

        if args.scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "modify_scenario",
                args,
                False,
                f"Scenario with ID '{args.scenario_id}' does not exist.",
            )

        scenario = self.map.simulated_scenarios[args.scenario_id]
        updated_fields = []
        if args.new_name is not None:
            scenario.name = args.new_name
            updated_fields.append("name")
        if args.new_summary_description is not None:
            scenario.summary_description = args.new_summary_description
            updated_fields.append("summary_description")
        if args.new_visual_description is not None:
            scenario.visual_description = args.new_visual_description
            updated_fields.append("visual_description")
        if args.new_narrative_context is not None:
            scenario.narrative_context = args.new_narrative_context
            updated_fields.append("narrative_context")
        if args.new_indoor_or_outdoor is not None:
            scenario.indoor_or_outdoor = args.new_indoor_or_outdoor
            updated_fields.append("indoor_or_outdoor")
        if args.new_type is not None:
            scenario.type = args.new_type
            updated_fields.append("type")
        if args.new_zone is not None:
            scenario.zone = args.new_zone
            updated_fields.append("zone")
        scenario.was_modified_this_run = True
        return self.map._log_and_summarize(
            "modify_scenario_in_simulation",
            args,
            True,
            f"Scenario '{args.scenario_id}' modified. Updated fields: {', '.join(updated_fields) if updated_fields else 'None'}.",
        )

    def delete_scenario(self, args: DeleteScenarioArgs) -> str:
        """Deletes the specified scenario."""

        if args.scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "delete_scenario",
                args,
                False,
                f"Scenario with ID '{args.scenario_id}' does not exist.",
            )

        for other_id, other_scenario in self.map.simulated_scenarios.items():
            for direction, exit_info in other_scenario.exits.items():
                if exit_info and exit_info.target_scenario_id == args.scenario_id:
                    other_scenario.exits[direction] = None

        if not self.map.simulated_scenarios[args.scenario_id].was_added_this_run:
            self.map.deleted_scenarios[args.scenario_id] = self.map.simulated_scenarios[args.scenario_id]

        del self.map.simulated_scenarios[args.scenario_id]
        self.map._compute_island_clusters()

        return self.map._log_and_summarize(
            "delete_scenario",
            args,
            True,
            f"Scenario '{args.scenario_id}' deleted successfully.",
        )

    def create_bidirectional_connection(self, args: CreateBidirectionalConnectionArgs) -> str:
        """Creates a new bidirectional connection between two existing scenarios."""

        if args.from_scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "create_bidirectional_connection",
                args,
                False,
                f"Error: Origin scenario ID '{args.from_scenario_id}' not fpund.",
            )
        if args.to_scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "create_bidirectional_connection",
                args,
                False,
                f"Error: Destination scenario ID '{args.to_scenario_id}' not found.",
            )
        if args.from_scenario_id == args.to_scenario_id:
            return self.map._log_and_summarize(
                "create_bidirectional_connection",
                args,
                False,
                "Error: Cannot connect a scenario to itself.",
            )

        origin_scenario = self.map.simulated_scenarios[args.from_scenario_id]
        destination_scenario = self.map.simulated_scenarios[args.to_scenario_id]

        for existing_direction, existing_exit in origin_scenario.exits.items():
            if existing_exit and existing_exit.target_scenario_id == args.to_scenario_id:
                return self.map._log_and_summarize(
                    "create_bidirectional_connection",
                    args,
                    False,
                    f"Error: Origin '{args.from_scenario_id}' has an existing exit via direction '{existing_direction}' to '{args.to_scenario_id}'. Cannot create another connection between them.",
                )

        direction_to_origin = OppositeDirections[args.direction_from_origin]

        if origin_scenario.exits.get(args.direction_from_origin) is not None:
            return self.map._log_and_summarize(
                "create_bidirectional_connection",
                args,
                False,
                f"Error: Origin scenario '{args.from_scenario_id}' already has an exit to the '{args.direction_from_origin}'.",
            )
        if destination_scenario.exits.get(direction_to_origin) is not None:
            return self.map._log_and_summarize(
                "create_bidirectional_connection",
                args,
                False,
                f"Error: Destination scenario '{args.to_scenario_id}' already has an exit to its '{direction_to_origin}' (which would be the return path).",
            )

        exit_info_origin = ExitInfo(
            target_scenario_id=args.to_scenario_id,
            connection_type=args.connection_type,
            travel_description=args.travel_description,
            traversal_conditions=args.traversal_conditions or [],
        )
        exit_info_destination = ExitInfo(
            target_scenario_id=args.from_scenario_id,
            connection_type=args.connection_type,
            travel_description=args.travel_description,
            traversal_conditions=args.traversal_conditions or [],
        )

        origin_scenario.exits[args.direction_from_origin] = exit_info_origin
        destination_scenario.exits[direction_to_origin] = exit_info_destination

        self.map._compute_island_clusters()
        return self.map._log_and_summarize(
            "create_bidirectional_connection",
            args,
            True,
            f"Connection type'{args.connection_type}' created: '{args.from_scenario_id}' ({args.direction_from_origin}) <-> '{args.to_scenario_id}' ({direction_to_origin}).",
        )

    def delete_bidirectional_connection(self, args: DeleteBidirectionalConnectionArgs) -> str:
        """Deletes a bidirectional connection starting from scenario_id_A in the specified direction."""

        if args.scenario_id_A not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "delete_bidirectional_connection",
                args,
                False,
                f"Error: Scenario A ID '{args.scenario_id_A}' not found.",
            )

        scenario_A = self.map.simulated_scenarios[args.scenario_id_A]
        exit_info_A_to_B = scenario_A.exits.get(args.direction_from_A)

        if not exit_info_A_to_B:
            return self.map._log_and_summarize(
                "delete_bidirectional_connection",
                args,
                False,
                f"Error: Scenario '{args.scenario_id_A}' has no exit to the '{args.direction_from_A}'.",
            )

        scenario_id_B = exit_info_A_to_B.target_scenario_id
        if scenario_id_B not in self.map.simulated_scenarios:
            scenario_A.exits[args.direction_from_A] = None
            self.map._compute_island_clusters()
            return self.map._log_and_summarize(
                "delete_bidirectional_connection",
                args,
                True,
                f"Exit from '{args.scenario_id_A}' ({args.direction_from_A}) cleared. Target scenario '{scenario_id_B}' was not found (map was possibly inconsistent).",
            )

        scenario_B = self.map.simulated_scenarios[scenario_id_B]
        direction_from_B = OppositeDirections[args.direction_from_A]

        scenario_A.exits[args.direction_from_A] = None
        exit_B_to_A = scenario_B.exits.get(direction_from_B)
        if exit_B_to_A and exit_B_to_A.target_scenario_id == args.scenario_id_A:
            scenario_B.exits[direction_from_B] = None
            message = f"Bidirectional connection '{args.scenario_id_A}' ({args.direction_from_A}) <-> '{scenario_id_B}' ({direction_from_B}) deleted."
        else:
            message = f"Exit from '{args.scenario_id_A}' ({args.direction_from_A}) to '{scenario_id_B}' deleted. Reverse connection from '{scenario_id_B}' not found or not pointing back as expected."

        self.map._compute_island_clusters()
        return self.map._log_and_summarize(
            "delete_bidirectional_connection",
            args,
            True,
            message,
        )

    def modify_bidirectional_connection(self, args: ModifyBidirectionalConnectionArgs) -> str:
        """Modifies attributes of an existing bidirectional connection."""

        if args.from_scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "modify_bidirectional_connection",
                args,
                False,
                f"Error: Origin scenario ID '{args.from_scenario_id}' not found.",
            )

        origin_scenario = self.map.simulated_scenarios[args.from_scenario_id]
        exit_info_origin = origin_scenario.exits.get(args.direction_from_origin)

        if not exit_info_origin:
            return self.map._log_and_summarize(
                "modify_bidirectional_connection",
                args,
                False,
                f"Error: Scenario '{args.from_scenario_id}' has no exit to the '{args.direction_from_origin}'.",
            )

        to_scenario_id = exit_info_origin.target_scenario_id
        if to_scenario_id not in self.map.simulated_scenarios:
            return self.map._log_and_summarize(
                "modify_bidirectional_connection",
                args,
                False,
                f"Exit from '{args.from_scenario_id}' ({args.direction_from_origin}) points to target scenario '{to_scenario_id}' not found.",
            )

        destination_scenario = self.map.simulated_scenarios[to_scenario_id]
        direction_to_origin = OppositeDirections[args.direction_from_origin]
        exit_info_destination = destination_scenario.exits.get(direction_to_origin)

        updated_fields_origin = []
        if args.new_connection_type is not None:
            exit_info_origin.connection_type = args.new_connection_type
            updated_fields_origin.append("connection_type")
        if args.new_travel_description is not None:
            exit_info_origin.travel_description = args.new_travel_description
            updated_fields_origin.append("travel_description")
        if args.new_traversal_conditions is not None:
            exit_info_origin.traversal_conditions = args.new_traversal_conditions
            updated_fields_origin.append("traversal_conditions")

        if exit_info_destination and exit_info_destination.target_scenario_id == args.from_scenario_id:
            if args.new_connection_type is not None:
                exit_info_destination.connection_type = args.new_connection_type
            if args.new_traversal_conditions is not None:
                exit_info_destination.traversal_conditions = args.new_traversal_conditions
            if args.new_travel_description is not None:
                exit_info_destination.travel_description = args.new_travel_description
            message = (
                f"Bidirectional connection from '{args.from_scenario_id}' ({args.direction_from_origin}) <-> '{to_scenario_id}' ({direction_to_origin}) modified. Updated fields: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
            )
        else:
            message = (
                f"Exit from '{args.from_scenario_id}' ({args.direction_from_origin}) modified. Reverse connection from '{to_scenario_id}' not found or not pointing back as expected. Updated fields on forward path: {', '.join(updated_fields_origin) if updated_fields_origin else 'None'}."
            )

        return self.map._log_and_summarize(
            "modify_bidirectional_connection",
            args,
            True,
            message,
        )

    def finalize_simulation(self, args: FinalizeSimulationArgs) -> str:
        self.map._compute_island_clusters()
        self.map.task_finalized_by_agent = True
        self.map.task_finalized_justification = args.justification
        return self.map._log_and_summarize("finalize_simulation", args, True, "Simulation finalized.")

    def validate_simulated_map(self, args: ValidateSimulationMapArgs) -> str:
        self.map.agent_validated = True
        self.map.agent_validation_conclusion_flag = args.does_map_meet_criteria
        self.map.agent_validation_assessment_reasoning = args.assessment_reasoning
        if args.suggested_improvements:
            self.map.agent_validation_suggested_improvements = args.suggested_improvements
        else:
            self.map.agent_validation_suggested_improvements = ""
        if self.map.agent_validation_conclusion_flag:
            return self.map._log_and_summarize(
                "validate_simulated_map",
                args,
                True,
                f"Simulated map meets all criteria. Reason: {args.assessment_reasoning}",
            )
        else:
            return self.map._log_and_summarize(
                "validate_simulated_map",
                args,
                True,
                f"Simulated doesn't meet all criteria. Reason: {args.assessment_reasoning}. Suggestions: {self.map.agent_validation_suggested_improvements}",
            )

    def get_summary_list(self) -> str:
        return self.map.get_summary_list()
