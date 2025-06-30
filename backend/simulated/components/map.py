from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Set, Literal, Tuple

from copy import deepcopy
from core_game.map.domain import GameMap, Scenario, Connection
from core_game.map.schemas import ScenarioModel, ConnectionModel
from core_game.map.constants import IndoorOrOutdoor, Direction, OppositeDirections

from core_game.character.domain import BaseCharacter, PlayerCharacter


class SimulatedMap:
    def __init__(self, game_map: GameMap) -> None:
        self._working_state: GameMap = game_map

    def __deepcopy__(self, memo):
        copied_game_map = GameMap(map_model=deepcopy(self._working_state.to_model()))
        new_copy = SimulatedMap(
            game_map=copied_game_map,
        )
        return new_copy

    def get_state(self) -> GameMap:
        return self._working_state

    
    def create_scenario(self,
        name: str,
        summary_description: str,
        visual_description: str,
        visual_prompt: str,
        narrative_context: str,
        indoor_or_outdoor: IndoorOrOutdoor,
        type: str,
        zone: str
    ) -> Scenario:
        """Create a new scenario in the simulated map and returns it."""

        scenario_model = ScenarioModel(
            name=name,
            summary_description=summary_description,
            visual_description=visual_description,
            visual_prompt=visual_prompt,
            narrative_context=narrative_context,
            indoor_or_outdoor=indoor_or_outdoor,
            type=type,
            zone=zone
        )
        scenario = Scenario(scenario_model)

        if self._working_state.find_scenario(scenario.id):
            raise ValueError(f"Internal Error, Scenario with ID {scenario.id} already exists.")

        self._working_state.add_scenario(scenario)

        return scenario

    
    def modify_scenario(self,
        scenario_id: str, new_name: Optional[str] = None,
        new_summary_description: Optional[str] = None,
        new_visual_description: Optional[str] = None,
        new_visual_prompt: Optional[str] = None,
        new_narrative_context: Optional[str] = None,
        new_indoor_or_outdoor: Optional[IndoorOrOutdoor] = None,
        new_type: Optional[str] = None,
        new_zone: Optional[str] = None,
    ) -> bool:
        """Modify an existing scenario in the simulated map. Returns True if modified, False if it does not exist."""

        result = self._working_state.modify_scenario(
            scenario_id,
            new_name,
            new_summary_description,
            new_visual_description,
            new_visual_prompt,
            new_narrative_context,
            new_indoor_or_outdoor,
            new_type,
            new_zone,
        )

        return result

    def find_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Return the scenario if it exists, or None otherwise."""
        return self._working_state.find_scenario(scenario_id)
    
    
    def delete_scenario(self, scenario_id: str) -> Scenario:
        """Delete a scenario from the simulated map. Returns True if deleted, False if it does not exist."""
        scenario = self._working_state.find_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario with ID '{scenario_id}' does not exist.")
        self._working_state.delete_scenario(scenario_id)
        return scenario

    
    
    def create_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction, 
        to_scenario_id: str,  
        connection_type: str,
        travel_description: Optional[str] = None,
        traversal_conditions: Optional[List[str]] = None,
    ) -> Connection:
        """Create a bidirectional connection between two scenarios. Returns the connection. Scenarios must have the exits available or it will raise an exception"""
        
        if from_scenario_id == to_scenario_id:
            raise ValueError("Cannot connect a scenario to itself.")

        origin_scenario = self._working_state.find_scenario(from_scenario_id)
        if not origin_scenario:
            raise KeyError(f"Origin scenario ID '{from_scenario_id}' not found.")

        destination_scenario = self._working_state.find_scenario(to_scenario_id)
        if not destination_scenario:
            raise KeyError(f"Destination scenario ID '{to_scenario_id}' not found.")

        for existing_direction, conn_id in origin_scenario.connections.items():
            if conn_id:
                conn = self._working_state.get_connection_by_id(conn_id)
                if conn and ((conn.scenario_a_id == from_scenario_id and conn.scenario_b_id == to_scenario_id) or
                            (conn.scenario_b_id == from_scenario_id and conn.scenario_a_id == to_scenario_id)):
                    raise ValueError(
                        f"Origin '{from_scenario_id}' already has an existing connection via direction '{existing_direction}' to '{to_scenario_id}'. Cannot create another connection between them."
                    )
        direction_to_origin = OppositeDirections[direction_from_origin]

        if origin_scenario.connections.get(direction_from_origin) is not None:
            raise ValueError(
                f"Origin scenario '{from_scenario_id}' already has a connection to the '{direction_from_origin}'."
            )

        if destination_scenario.connections.get(direction_to_origin) is not None:
            raise ValueError(
                f"Destination scenario '{to_scenario_id}' already has a connection to its '{direction_to_origin}' (which would be the return path)."
            )
        
        
        connection_model = ConnectionModel(
            scenario_a_id=from_scenario_id,
            scenario_b_id=to_scenario_id,
            direction_from_a=direction_from_origin,
            connection_type=connection_type,
            travel_description=travel_description,
            traversal_conditions=traversal_conditions or [],
        )

        connection = Connection(connection_model)
        connection = self._working_state.add_connection(connection)
        if not connection:
            raise ValueError("Something unexpected went wrong")
        return connection
    
    
    def delete_bidirectional_connection(self, scenario_id_A: str, direction_from_A: Direction)->Connection:
        """Delete a bidirectional connection from scenario A in the specified direction."""
        scenario_A = self._working_state.find_scenario(scenario_id_A)
        if not scenario_A:
            raise KeyError(f"Scenario A ID '{scenario_id_A}' not found.")

        conn_id = scenario_A.connections.get(direction_from_A)
        if conn_id is None:
            raise KeyError(f"Scenario '{scenario_id_A}' has no connection to the '{direction_from_A}'.")

        connection = self._working_state.delete_bidirectional_connection(conn_id)
        if connection is None:
            raise KeyError(f"Scenario '{scenario_id_A}' has no connection to the '{direction_from_A}'.")
        return connection

    
    def modify_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction,
        new_connection_type: Optional[str] = None,
        new_travel_description: Optional[str] = None,
        new_traversal_conditions: Optional[List[str]] = None
    ) -> None:
        """Modify an existing bidirectional connection."""

        from_scenario = self._working_state.find_scenario(from_scenario_id)
        if not from_scenario:
            raise KeyError(f"Origin scenario ID '{from_scenario_id}' not found.")

        connection_id = from_scenario.connections.get(direction_from_origin)
        if not connection_id:
            raise KeyError(f"Scenario '{from_scenario_id}' has no connection to the '{direction_from_origin}'.")
        
        success = self._working_state.modify_bidirectional_connection(
            connection_id,
            new_connection_type,
            new_travel_description,
            new_traversal_conditions
        )
        if not success:
            raise ValueError("Something unexpected went wrong")

    def get_connection(
        self, scenario_id: str, direction_from: Direction
    ) -> Optional[Connection]:
        """
        Given a scenario id and direction, returns the Connection or None if not found.
        """
        return self._working_state.get_connection(scenario_id,direction_from)
    
    def get_scenario_count(self)->int:
        """
        Returns the number of scenarios.
        """
        return self._working_state.get_scenario_count()
    
    def get_cluster_summary(self, list_all_scenarios: bool, max_listed_per_cluster: Optional[int] = 5) -> str:
        """
        Generates a formatted string summarizing connectivity clusters.
        Lists all scenarios (ID and name) per cluster if list_all_scenarios is True.
        Otherwise, lists up to 'max_listed_per_cluster' scenarios per cluster.
        """
        return self._working_state.get_cluster_summary(list_all_scenarios,max_listed_per_cluster)

    def get_summary_list(self)->str:
        """Returns a string that represents a summary of scenarios and clusters"""
        return self.get_cluster_summary(list_all_scenarios=False, max_listed_per_cluster=2)
    
    def find_scenarios_by_attribute(self,attribute_to_filter: Literal["type", "name_contains", "zone", "indoor_or_outdoor"],value_to_match: str)->List[Scenario]:
        """Returns a list of filtered scenarios by an attribute"""
        return self._working_state.find_scenarios_by_attribute(attribute_to_filter,value_to_match)

    def can_place_player(self, player: PlayerCharacter, scenario_id: str) -> Tuple[bool,str]:
        """Checks if it can place the player to a certain scenario. Returns result and message in case of negative result"""
        if not self._working_state.find_scenario(scenario_id=scenario_id):
            return (False, f"Scenario with ID '{scenario_id}' does not exist.")
        else:
            return (True, "")

    def can_place_character(self, character: BaseCharacter, scenario_id: str) -> Tuple[bool,str]:
        """Checks if it can place the player to a certain scenario. Returns result and message in case of negative result"""
        if not self._working_state.find_scenario(scenario_id=scenario_id):
            return (False, f"Scenario with ID '{scenario_id}' does not exist.")
        else:
            return (True, "")

    
    def place_player(self, player: PlayerCharacter, scenario_id: str)->Scenario:
        scenario=self._working_state.place_player(player, scenario_id)
        if not scenario:
            raise KeyError(f"Scenario with ID '{scenario_id}' does not exist.")
        
        return scenario
    
    
    def place_character(self, character: BaseCharacter, scenario_id: str)->Scenario:              
        scenario=self._working_state.place_character(character, scenario_id)
        if not scenario:
            raise KeyError(f"Scenario with ID '{scenario_id}' does not exist.")
        
        return scenario
    
    
    def try_remove_character_from_scenario(self, character: BaseCharacter, scenario_id: str)->Scenario:
        scenario = self._working_state.find_scenario(scenario_id)
        if not scenario:
            raise KeyError(f"Scenario with ID '{scenario_id}' does not exist.")
        scenario = self._working_state.remove_character_from_scenario(character, scenario_id)
        if not scenario:
            raise KeyError(f"Scenario with ID '{scenario_id}' does not exist.")
        return scenario