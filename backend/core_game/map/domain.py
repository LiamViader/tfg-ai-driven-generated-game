from core_game.map.schemas import ScenarioModel, ScenarioSnapshot, ConnectionModel, GameMapModel
from typing import Dict, Optional, List, Set, Literal
from core_game.map.constants import Direction, OppositeDirections, IndoorOrOutdoor
from core_game.time.domain import GameTime

class Scenario:
    def __init__(self, scenario_model: ScenarioModel):
        self._data: ScenarioModel = scenario_model
    
    @property
    def id(self) -> str:
        return self._data.id

    @property
    def name(self) -> str:
        return self._data.name

    @name.setter
    def name(self, value: str) -> None:
        self._data.name = value

    @property
    def visual_description(self) -> str:
        return self._data.visual_description

    @visual_description.setter
    def visual_description(self, value: str) -> None:
        self._data.visual_description = value

    @property
    def narrative_context(self) -> str:
        return self._data.narrative_context

    @narrative_context.setter
    def narrative_context(self, value: str) -> None:
        self._data.narrative_context = value

    @property
    def summary_description(self) -> str:
        return self._data.summary_description

    @summary_description.setter
    def summary_description(self, value: str) -> None:
        self._data.summary_description = value

    @property
    def indoor_or_outdoor(self) -> IndoorOrOutdoor:
        return self._data.indoor_or_outdoor

    @indoor_or_outdoor.setter
    def indoor_or_outdoor(self, value: IndoorOrOutdoor) -> None:
        self._data.indoor_or_outdoor = value

    @property
    def type(self) -> str:
        return self._data.type

    @type.setter
    def type(self, value: str) -> None:
        self._data.type = value

    @property
    def zone(self) -> str:
        return self._data.zone

    @zone.setter
    def zone(self, value: str) -> None:
        self._data.zone = value

    @property
    def connections(self) -> dict:
        return self._data.connections

    @property
    def valid_from(self) -> Optional[float]:
        return self._data.valid_from

    @property
    def previous_versions(self) -> list:
        return self._data.previous_versions

    def snapshot_scenario(self, current_time: float):
        snapshot = ScenarioSnapshot(
            name=self._data.name,
            visual_description=self._data.visual_description,
            narrative_context=self._data.narrative_context,
            summary_description=self._data.summary_description,
            indoor_or_outdoor=self._data.indoor_or_outdoor,
            type=self._data.type,
            zone=self._data.zone,
            connections=self._data.connections.copy(),
            valid_from=self._data.valid_from,
            valid_until=current_time
        )
        self._data.valid_from = current_time
        self._data.previous_versions.append(snapshot)

    def get_scenario_model(self) -> ScenarioModel:
        """Return the underlying scenario model."""
        return self._data

class Connection:
    def __init__(self, connection_model: ConnectionModel):
        self._data: ConnectionModel = connection_model
    
    @property
    def id(self) -> str:
        return self._data.id

    @property
    def scenario_a_id(self) -> str:
        return self._data.scenario_a_id

    @property
    def scenario_b_id(self) -> str:
        return self._data.scenario_b_id

    @property
    def direction_from_a(self) -> Direction:
        return self._data.direction_from_a

    @property
    def connection_type(self) -> str:
        return self._data.connection_type

    @connection_type.setter
    def connection_type(self, value: str) -> None:
        self._data.connection_type = value

    @property
    def travel_description(self) -> Optional[str]:
        return self._data.travel_description

    @travel_description.setter
    def travel_description(self, value: Optional[str]) -> None:
        self._data.travel_description = value

    @property
    def traversal_conditions(self) -> List[str]:
        return self._data.traversal_conditions

    @traversal_conditions.setter
    def traversal_conditions(self, value: List[str]) -> None:
        self._data.traversal_conditions = value

    @property
    def exit_appearance_description(self) -> Optional[str]:
        return self._data.exit_appearance_description

    @exit_appearance_description.setter
    def exit_appearance_description(self, value: Optional[str]) -> None:
        self._data.exit_appearance_description = value

    @property
    def is_blocked(self) -> bool:
        return self._data.is_blocked

    @is_blocked.setter
    def is_blocked(self, value: bool) -> None:
        self._data.is_blocked = value

    @property
    def direction_from_b(self) -> Direction:
        """Return the direction from scenario B towards scenario A."""
        return OppositeDirections[self.direction_from_a]

    def get_other_scenario_id(self, scenario_id: str) -> str:
        """Given one scenario id, return the id of the other scenario in the connection."""
        if scenario_id == self.scenario_a_id:
            return self.scenario_b_id
        elif scenario_id == self.scenario_b_id:
            return self.scenario_a_id
        else:
            raise ValueError(f"Scenario id '{scenario_id}' is not part of this connection.")

    def get_direction_from(self, scenario_id: str) -> Direction:
        """Given a scenario id, return the direction from that scenario to the other scenario."""
        if scenario_id == self.scenario_a_id:
            return self.direction_from_a
        elif scenario_id == self.scenario_b_id:
            return OppositeDirections[self.direction_from_a]
        else:
            raise ValueError(f"Scenario id '{scenario_id}' is not part of this connection.")

    def get_direction_to(self, from_scenario_id: str) -> Direction:
        """
        Given a scenario id of origin, return the direction from the other scenario to origin (opposite of get_direction_from).
        """
        direction_from = self.get_direction_from(from_scenario_id)
        return OppositeDirections[direction_from]

    def get_connection_model(self) -> ConnectionModel:
        """Return the underlying connection model."""
        return self._data


class GameMap():
    def __init__(self, map_model: Optional[GameMapModel] = None):
        self._scenarios: Dict[str, Scenario]
        self._connections: Dict[str, Connection]
        self._island_clusters: List[Set[str]]

        if map_model:
            self._populate_from_model(map_model)
        else:
            self._scenarios = {}
            self._connections = {}
            self._island_clusters = []

    def _populate_from_model(self, model: GameMapModel):
        self._scenarios = {scenario.id: Scenario(scenario) for scenario in model.scenarios.values()}
        self._connections = {connection.id: Connection(connection) for connection in model.connections.values()}
        self._island_clusters = []
        self._compute_island_clusters()

    def _compute_island_clusters(self) -> None:
        """Computes the clusters formed by scenarios in the map"""
        visited = set()
        clusters = []
        for scenario_id in self._scenarios:
            if scenario_id not in visited:
                cluster = set()
                to_visit = [scenario_id]
                while to_visit:
                    current = to_visit.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.add(current)
                        conns = self._scenarios[current].connections
                        connected_ids = []
                        for conn_id in conns.values():
                            if conn_id:
                                conn = self._connections.get(conn_id)
                                if not conn:
                                    continue
                                other_id = conn.get_other_scenario_id(current)
                                if other_id in self._scenarios:
                                    connected_ids.append(other_id)
                        
                        to_visit.extend([sid for sid in connected_ids if sid not in visited])
                clusters.append(cluster)
        self._island_clusters = clusters

    def to_model(self) -> GameMapModel:
        """Converts the domain GameMap back into a Pydantic model."""
        return GameMapModel(
            scenarios={sid: scenario.get_scenario_model() for sid, scenario in self._scenarios.items()},
            connections={cid: conn.get_connection_model() for cid, conn in self._connections.items()}
        )
    
    def create_scenario(self,
        name: str, 
        summary_description: str, 
        visual_description: str,
        narrative_context: str, 
        indoor_or_outdoor: IndoorOrOutdoor,
        type: str, 
        zone: str
    ) -> Scenario:
        """Create a new scenario in map and return it."""

        scenario_model = ScenarioModel(
            name=name,
            visual_description=visual_description,
            narrative_context=narrative_context,
            summary_description=summary_description,
            indoor_or_outdoor=indoor_or_outdoor,
            zone=zone,
            type=type,
        )
        if scenario_model.id in self._scenarios:
            raise ValueError(f"Internal Error, Scenario with ID {scenario_model.id} already exists.")

        scenario = Scenario(scenario_model)
        self._scenarios[scenario.id] = scenario
        self._island_clusters.append({scenario.id})

        return scenario
    
    def modify_scenario(self, 
        scenario_id: str, new_name: Optional[str] = None,
        new_summary_description: Optional[str] = None,
        new_visual_description: Optional[str] = None,
        new_narrative_context: Optional[str] = None,
        new_indoor_or_outdoor: Optional[IndoorOrOutdoor] = None,
        new_type: Optional[str] = None, 
        new_zone: Optional[str] = None,
    ) -> bool:
        """Modify an existing scenario. Returns True if modified, False if it does not exist."""

        if scenario_id not in self._scenarios:
            return False

        scenario_to_modify = self._scenarios[scenario_id]

        if new_name is not None:
            scenario_to_modify.name = new_name
        if new_summary_description is not None:
            scenario_to_modify.summary_description = new_summary_description
        if new_visual_description is not None:
            scenario_to_modify.visual_description = new_visual_description
        if new_narrative_context is not None:
            scenario_to_modify.narrative_context = new_narrative_context
        if new_indoor_or_outdoor is not None:
            scenario_to_modify.indoor_or_outdoor = new_indoor_or_outdoor
        if new_type is not None:
            scenario_to_modify.type = new_type
        if new_zone is not None:
            scenario_to_modify.zone = new_zone

        return True

    def find_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Return the scenario if it exists, or None otherwise."""
        return self._scenarios.get(scenario_id)
    
    def delete_scenario(self, scenario_id: str) -> bool:
        """Delete a scenario. Returns True if deleted, False if it does not exist."""

        if scenario_id not in self._scenarios:
            return False

        for other_id, other_scenario in self._scenarios.items():
            for direction, conn_id in other_scenario.connections.items():
                if conn_id:
                    conn = self._connections.get(conn_id)
                    if conn and (conn.scenario_a_id == scenario_id or conn.scenario_b_id == scenario_id):
                        other_scenario.connections[direction] = None
                        self._connections.pop(conn_id, None)

        del self._scenarios[scenario_id]
        self._compute_island_clusters()

        return True
    
    def create_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction, 
        to_scenario_id: str,  
        connection_type: str,
        travel_description: Optional[str] = None,
        traversal_conditions: Optional[List[str]] = None,
    ) -> Connection:
        """Create a bidirectional connection between two scenarios. Returns the connection. Scenarios must have the exits available or it will raise an exception"""
        

        if from_scenario_id not in self._scenarios:
            raise KeyError(f"Origin scenario ID '{from_scenario_id}' not found.")

        if to_scenario_id not in self._scenarios:
            raise KeyError(f"Destination scenario ID '{to_scenario_id}' not found.")

        if from_scenario_id == to_scenario_id:
            raise ValueError("Cannot connect a scenario to itself.")

        origin_scenario = self._scenarios[from_scenario_id]
        destination_scenario = self._scenarios[to_scenario_id]

        for existing_direction, conn_id in origin_scenario.connections.items():
            if conn_id:
                conn = self._connections.get(conn_id)
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

        self._connections[connection.id] = connection
        origin_scenario.connections[direction_from_origin] = connection.id
        destination_scenario.connections[direction_to_origin] = connection.id

        self._compute_island_clusters()

        return connection
    
    def delete_bidirectional_connection(self, scenario_id_A: str, direction_from_A: Direction)->None:
        """Delete a bidirectional connection from scenario A in the specified direction."""
        
        if scenario_id_A not in self._scenarios:
            raise KeyError(f"Scenario A ID '{scenario_id_A}' not found.")


        scenario_A = self._scenarios[scenario_id_A]
        conn_id_A_to_B = scenario_A.connections.get(direction_from_A)
        conn = self._connections.get(conn_id_A_to_B) if conn_id_A_to_B else None

        if conn is None:
            raise KeyError(f"Scenario '{scenario_id_A}' has no connection to the '{direction_from_A}'.")

        scenario_id_B = conn.get_other_scenario_id(scenario_id_A)
        if scenario_id_B not in self._scenarios:
            scenario_A.connections[direction_from_A] = None
            self._connections.pop(conn.id, None)
            self._compute_island_clusters()
            return

        scenario_B = self._scenarios[scenario_id_B]
        direction_from_B = OppositeDirections[direction_from_A]

        scenario_A.connections[direction_from_A] = None

        scenario_B.connections[direction_from_B] = None
        self._connections.pop(conn.id, None)

        self._compute_island_clusters()
    
    def modify_bidirectional_connection(self, 
        from_scenario_id: str, 
        direction_from_origin: Direction,
        new_connection_type: Optional[str] = None,
        new_travel_description: Optional[str] = None,
        new_traversal_conditions: Optional[List[str]] = None
    ) -> None:
        """Modify an existing bidirectional connection."""

        if from_scenario_id not in self._scenarios:
            raise KeyError(f"Origin scenario ID '{from_scenario_id}' not found.")

        origin_scenario = self._scenarios[from_scenario_id]
        conn_id_origin = origin_scenario.connections.get(direction_from_origin)
        conn_origin = self._connections.get(conn_id_origin) if conn_id_origin else None

        if conn_origin is None:
            raise KeyError(f"Scenario '{from_scenario_id}' has no connection to the '{direction_from_origin}'.")

        if new_connection_type is not None:
            conn_origin.connection_type = new_connection_type
        if new_travel_description is not None:
            conn_origin.travel_description = new_travel_description
        if new_traversal_conditions is not None:
            conn_origin.traversal_conditions = new_traversal_conditions

    def get_connection(
        self, scenario_id: str, direction_from: Direction
    ) -> Optional[Connection]:
        """
        Given a scenario id and direction, returns the Connection or None if not found.
        """
        scenario = self._scenarios.get(scenario_id)
        if not scenario:
            return None
        conn_id = scenario.connections.get(direction_from)
        if not conn_id:
            return None
        return self._connections.get(conn_id)
    
    def get_scenario_count(self)->int:
        """
        Returns the number of scenarios.
        """
        return len(self._scenarios)
    
    def find_scenarios_by_attribute(self,attribute_to_filter: Literal["type", "name_contains", "zone", "indoor_or_outdoor"],value_to_match: str)->List[Scenario]:
        """Returns a list of filtered scenarios by an attribute"""
        matches = []
        value_to_match_lower = value_to_match.lower()

        for scenario in self._scenarios.values():
            if attribute_to_filter == "type" and getattr(scenario, 'type', '').lower() == value_to_match_lower:
                matches.append(scenario)
            elif attribute_to_filter == "indoor_or_outdoor" and getattr(scenario, 'indoor_or_outdoor', '').lower() == value_to_match_lower:
                matches.append(scenario)
            elif attribute_to_filter == "name_contains" and value_to_match_lower in scenario.name.lower():
                matches.append(scenario)
            elif attribute_to_filter == "zone" and getattr(scenario, 'zone', '').lower() == value_to_match_lower:
                matches.append(scenario)

        return matches
    
    def get_cluster_summary(self, list_all_scenarios: bool, max_listed_per_cluster: Optional[int] = 5) -> str:
        """
        Generates a formatted string summarizing connectivity clusters.
        Lists all scenarios (ID and name) per cluster if list_all_scenarios is True.
        Otherwise, lists up to 'max_listed_per_cluster' scenarios per cluster.
        """
        if not self._island_clusters:
            return "The simulated map currently has 0 scenarios."
        
        summary_lines = [
            f"The simulated map has {len(self._scenarios)} scenarios and {len(self._island_clusters)} cluster(s) of scenarios:"
        ]
        for i, cluster_set in enumerate(self._island_clusters, 1):
            cluster_list_sorted = sorted(list(cluster_set))
            num_to_display = len(cluster_list_sorted) if list_all_scenarios else (
                max_listed_per_cluster or len(cluster_list_sorted)
            )

            scenario_lines: List[str] = []
            for k, scenario_id in enumerate(cluster_list_sorted):
                if k < num_to_display:
                    scenario = self._scenarios.get(scenario_id)
                    if scenario:
                        scenario_lines.append(f"  - \"{scenario.name}\" (ID: {scenario.id})")
                else:
                    break

            if not list_all_scenarios and len(cluster_list_sorted) > num_to_display:
                scenario_lines.append(
                    f"  - ...and {len(cluster_list_sorted) - num_to_display} more."
                )

            if scenario_lines:
                summary_lines.append(
                    f"- Cluster {i} (contains {len(cluster_list_sorted)} scenarios):\n" + "\n".join(scenario_lines)
                )
            else:
                summary_lines.append(
                    f"- Cluster {i} (contains {len(cluster_list_sorted)} scenarios): (No scenarios found for this cluster - this might indicate an issue)."
                )

        return "\n".join(summary_lines)