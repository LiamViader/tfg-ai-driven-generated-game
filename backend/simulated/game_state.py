from core_game.game.singleton import GameStateSingleton
from core_game.game.domain import GameState
from simulated.map import SimulatedMap
from simulated.characters import SimulatedCharacters
from simulated.layer import SimulationLayer
from typing import List

class SimulatedGameState:
    """
    Class to handle the game state in a simulated environment where agents can interact it. 
    It is used to store and manipulate the game state during simulations. 
    So it doesnt modify the real game state directly.
    """
    def __init__(self, game_state: GameState):
        self._map = SimulatedMap(game_state.game_map, self)
        self._characters = SimulatedCharacters(game_state.characters, self)
        self._layers: List[SimulationLayer] = []

    #CONTROL DE VERSIONS

    def begin_layer(self):
        parent = self._layers[-1] if self._layers else None
        self._layers.append(SimulationLayer(parent=parent, base_state=self))

    def current_layer(self) -> SimulationLayer:
        if not self._layers:
            self.begin_layer()
        return self._layers[-1]

    @property
    def base_map(self) -> SimulatedMap:
        return self._map
    
    @property
    def base_characters(self) -> SimulatedCharacters:
        return self._characters

    def modify_map(self) -> SimulatedMap:
        return self.current_layer().modify_map()

    def modify_characters(self) -> SimulatedCharacters:
        return self.current_layer().modify_characters()

    def commit(self):
        layer = self._layers.pop()
        parent = self._layers[-1] if self._layers else None

        if layer.has_modified_map():
            if parent:
                parent.set_modified_map(layer.get_modified_map())
            else:
                self._map = layer.get_modified_map()

        if layer.has_modified_characters():
            if parent:
                parent.set_modified_characters(layer.get_modified_characters())
            else:
                self._characters = layer.get_modified_characters()

    def rollback(self):
        self._layers.pop()

    # ---- METODES MAPA ------

    #METODES DE MODIFICACIO
    def create_scenario(self, *args, **kwargs):
        return self.modify_map().create_scenario(*args, **kwargs)

    def modify_scenario(self, *args, **kwargs):
        return self.modify_map().modify_scenario(*args, **kwargs)

    def delete_scenario(self, scenario_id: str):
        return self.modify_map().delete_scenario(scenario_id)

    def create_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().create_bidirectional_connection(*args, **kwargs)

    def delete_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().delete_bidirectional_connection(*args, **kwargs)

    def modify_bidirectional_connection(self, *args, **kwargs):
        return self.modify_map().modify_bidirectional_connection(*args, **kwargs)

    def place_player(self, *args, **kwargs):
        return self.modify_map().place_player(*args, **kwargs)

    def place_character(self, *args, **kwargs):
        return self.modify_map().place_character(*args, **kwargs)
    
    def remove_character_from_scenario(self, *args, **kwargs):
        return self.modify_map().remove_character_from_scenario(*args, **kwargs)

    # METODES DE LECTURA
    def find_scenario(self, scenario_id: str):
        return self.current_layer().map.find_scenario(scenario_id)

    def get_connection(self, scenario_id: str, direction_from):
        return self.current_layer().map.get_connection(scenario_id, direction_from)

    def get_scenario_count(self):
        return self.current_layer().map.get_scenario_count()

    def get_cluster_summary(self, *args, **kwargs):
        return self.current_layer().map.get_cluster_summary(*args, **kwargs)

    def get_summary_list(self):
        return self.current_layer().map.get_summary_list()

    def find_scenarios_by_attribute(self, *args, **kwargs):
        return self.current_layer().map.find_scenarios_by_attribute(*args, **kwargs)

    def can_place_player(self, *args, **kwargs):
        return self.current_layer().map.can_place_player(*args, **kwargs)

    def can_place_character(self, *args, **kwargs):
        return self.current_layer().map.can_place_character(*args, **kwargs)


class SimulatedGameStateSingleton:
    """ Singleton class to manage the simulated game state.
    This class ensures that only one instance of SimulatedGameState exists at any time."""
    _instance: SimulatedGameState | None = None

    @classmethod
    def get_instance(cls): 
        """
        Returns the singleton instance of SimulatedGameState.
        If it doesn't exist, it creates a new one.
        """
        if cls._instance is None:
            cls._instance = SimulatedGameState(GameStateSingleton.get_instance())
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """
        Resets the singleton instance of SimulatedGameState.
        This is useful for starting a new simulation without interference from previous states.
        """
        cls._instance = SimulatedGameState(GameStateSingleton.get_instance())