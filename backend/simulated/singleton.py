from core_game.game_state.singleton import GameStateSingleton
from versioning.layers.manager import GameStateVersionManager 
from simulated.game_state import SimulatedGameState
from versioning.deltas.manager import StateCheckpointManager
import typing 
from versioning.deltas.factory import CheckpointManagerFactory

class SimulatedGameStateSingleton:
    """
    Singleton that orchestrates the simulated state and its versioning.
    
    - Provides global access to an instance of the facade (SimulatedGameState).
    - Internally manages the transaction lifecycle (commit/rollback).
    """
    _version_manager_instance: typing.Optional[GameStateVersionManager] = None
    _facade_instance: typing.Optional[SimulatedGameState] = None
    _checkpoint_manager: typing.Optional[StateCheckpointManager] = None

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
        cls._checkpoint_manager = None
        cls._initialize()

    @classmethod
    def get_checkpoint_manager(cls) -> StateCheckpointManager:
        """Return the global StateCheckpointManager instance."""
        cls._initialize()
        if cls._checkpoint_manager is None:
            factory = CheckpointManagerFactory()
            cls._checkpoint_manager = factory.create_manager(cls.get_instance())
        return cls._checkpoint_manager