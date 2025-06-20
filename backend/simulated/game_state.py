from core_game.game.singleton import GameStateSingleton
from core_game.game.domain import GameState
from simulated.map import SimulatedMap
from simulated.characters import SimulatedCharacters

class SimulatedGameState:
    """
    Class to handle the game state in a simulated environment where agents can interact it. 
    It is used to store and manipulate the game state during simulations. 
    So it doesnt modify the real game state directly.
    """
    def __init__(self, game_state: GameState):
        """
        Initializes the simulated game state with a the provided game state model.
        :param game_state: The original game state model to simulate.
        """
        self._simulated_map: SimulatedMap = SimulatedMap(game_state.game_map, self)
        self._simulated_characters: SimulatedCharacters = SimulatedCharacters(game_state.characters, self)
    
    @property
    def simulated_map(self)-> SimulatedMap:
        return self._simulated_map

    @property
    def simulated_characters(self) -> SimulatedCharacters:
        return self._simulated_characters

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