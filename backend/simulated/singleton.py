# in: core/singleton.py

from core_game.game_state.singleton import GameStateSingleton
from simulated.versioning.manager import GameStateVersionManager 
from simulated.game_state import SimulatedGameState             
import typing 

class SimulatedGameStateSingleton:
    """
    Singleton that orchestrates the simulated state and its versioning.
    
    - Provides global access to an instance of the facade (SimulatedGameState).
    - Internally manages the transaction lifecycle (commit/rollback).
    """
    _version_manager_instance: typing.Optional[GameStateVersionManager] = None
    _facade_instance: typing.Optional[SimulatedGameState] = None

    @classmethod
    def _initialize(cls):
        """Initializes the internal instances if they don't exist yet."""
        if cls._version_manager_instance is None:
            game_state = GameStateSingleton.get_instance()
            cls._version_manager_instance = GameStateVersionManager(game_state)
        
        if cls._facade_instance is None:
            cls._facade_instance = SimulatedGameState(cls._version_manager_instance)

    @classmethod
    def get_instance(cls) -> SimulatedGameState:
        """
        Returns the unique instance of the SimulatedGameState facade.
        All state reads and modifications are performed through this object.
        """
        cls._initialize()
        assert cls._facade_instance is not None, "Initialization of facade failed."
        return cls._facade_instance

    # --- DELEGATED TRANSACTION METHODS ---

    @classmethod
    def begin_transaction(cls):
        """Starts a new simulation layer (transaction)."""
        cls._initialize()
        assert cls._version_manager_instance is not None, "Initialization of version manager failed."
        cls._version_manager_instance.begin_transaction()

    @classmethod
    def commit(cls):
        """Commits the changes from the current layer."""
        cls._initialize()
        assert cls._version_manager_instance is not None, "Initialization of version manager failed."
        cls._version_manager_instance.commit()

    @classmethod
    def rollback(cls):
        """Discards the changes from the current layer."""
        cls._initialize()
        assert cls._version_manager_instance is not None, "Initialization of version manager failed."
        cls._version_manager_instance.rollback()
        
    @classmethod
    def reset_instance(cls):
        """
        Completely resets the simulated state to its original base state.
        """
        cls._version_manager_instance = None
        cls._facade_instance = None
        cls._initialize()