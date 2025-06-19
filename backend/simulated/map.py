from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Generic, TypeVar, Callable, Set, Literal
from copy import deepcopy
from core_game.map.schemas import GameMapModel
from core_game.map.domain import GameMap, Scenario, Connection
from core_game.map.constants import IndoorOrOutdoor, Direction


class SimulatedMap:
    def __init__(self, game_map_model: GameMap) -> None:
        self._original_state: GameMap = game_map_model
        self._copied_state: GameMap | None = None
        self._working_state: GameMap = self._original_state
        self.is_modified: bool = False
        self._deleted_scenarios: Dict[str, Scenario] = {}
        self._modified_scenarios: Set[str] = set() 
        self._added_scenarios: Set[str] = set()
    
    @property
    def working_state(self) -> GameMap:
        return self._working_state
    
    def _started_modifying(self) -> None:
        """Mark the map as modified and create a copy if not already done."""
        if not self.is_modified:
            self._copied_state = GameMap(map_model=deepcopy(self._original_state.to_model()))
            self.is_modified = True
            self._working_state = self._copied_state

    def create_scenario(self,
        name: str, 
        summary_description: str, 
        visual_description: str,
        narrative_context: str, 
        indoor_or_outdoor: IndoorOrOutdoor,
        type: str, 
        zone: str
    ) -> Optional[str]:
        """Create a new scenario in the simulated map and return its ID."""
        
        self._started_modifying()

        scenario = self.working_state.create_scenario(
            name,
            summary_description,
            visual_description,
            narrative_context,
            indoor_or_outdoor,
            type,
            zone
        )

        self._added_scenarios.add(scenario.id)

        return scenario.id

    def modify_scenario(self, 
        scenario_id: str, new_name: Optional[str] = None,
        new_summary_description: Optional[str] = None,
        new_visual_description: Optional[str] = None,
        new_narrative_context: Optional[str] = None,
        new_indoor_or_outdoor: Optional[IndoorOrOutdoor] = None,
        new_type: Optional[str] = None, 
        new_zone: Optional[str] = None,
    ) -> bool:
        """Modify an existing scenario in the simulated map. Returns True if modified, False if it does not exist."""
        
        self._started_modifying()

        result = self.working_state.modify_scenario(
            scenario_id,
            new_name,
            new_summary_description,
            new_visual_description,
            new_narrative_context,
            new_indoor_or_outdoor,
            new_type, 
            new_zone,
        )

        if result:
            self._modified_scenarios.add(scenario_id)

        return result

    def find_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Return the scenario if it exists, or None otherwise."""
        return self.working_state.find_scenario(scenario_id)
    

    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario from the simulated map. Returns True if deleted, False if it does not exist."""
        
        self._started_modifying()

        result = self.working_state.delete_scenario(scenario_id)

        if result and scenario_id not in self._added_scenarios:
            scenario = self.working_state.find_scenario(scenario_id)
            if scenario:
                self._deleted_scenarios[scenario_id] = scenario

        return result
    
    def create_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction, 
        to_scenario_id: str,  
        connection_type: str,
        travel_description: Optional[str] = None,
        traversal_conditions: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Create a bidirectional connection between two scenarios."""
        
        self._started_modifying()

        connection = self.working_state.create_bidirectional_connection(
            from_scenario_id,
            direction_from_origin,
            to_scenario_id,
            connection_type,
            travel_description,
            traversal_conditions
        )

        return connection.id
    
    def delete_bidirectional_connection(self, scenario_id_A: str, direction_from_A: Direction)->None:
        """Delete a bidirectional connection from scenario A in the specified direction."""
        
        self._started_modifying()
        self.working_state.delete_bidirectional_connection(scenario_id_A,direction_from_A)


    def modify_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction,
        new_connection_type: Optional[str] = None,
        new_travel_description: Optional[str] = None,
        new_traversal_conditions: Optional[List[str]] = None
    ) -> None:
        """Modify an existing bidirectional connection."""

        self._started_modifying()
        self.working_state.modify_bidirectional_connection(
            from_scenario_id,
            direction_from_origin,
            new_connection_type,
            new_travel_description,
            new_traversal_conditions
        )


    def get_connection(
        self, scenario_id: str, direction_from: Direction
    ) -> Optional[Connection]:
        """
        Given a scenario id and direction, returns the Connection or None if not found.
        """
        return self.working_state.get_connection(scenario_id,direction_from)
    
    def get_scenario_count(self)->int:
        """
        Returns the number of scenarios.
        """
        return self.working_state.get_scenario_count()
    
    def get_cluster_summary(self, list_all_scenarios: bool, max_listed_per_cluster: Optional[int] = 5) -> str:
        """
        Generates a formatted string summarizing connectivity clusters.
        Lists all scenarios (ID and name) per cluster if list_all_scenarios is True.
        Otherwise, lists up to 'max_listed_per_cluster' scenarios per cluster.
        """
        return self.working_state.get_cluster_summary(list_all_scenarios,max_listed_per_cluster)

    def get_summary_list(self)->str:
        """Returns a string that represents a summary of scenarios and clusters"""
        return self.get_cluster_summary(list_all_scenarios=False, max_listed_per_cluster=2)
    
    def find_scenarios_by_attribute(self,attribute_to_filter: Literal["type", "name_contains", "zone", "indoor_or_outdoor"],value_to_match: str)->List[Scenario]:
        """Returns a list of filtered scenarios by an attribute"""
        return self.working_state.find_scenarios_by_attribute(attribute_to_filter,value_to_match)
