from .domain import GameState

class GameStateSingleton:
    _instance: GameState | None = None

    @classmethod
    def get_instance(cls) -> GameState:
        if cls._instance is None:
            cls._instance = GameState()
            cls._instance.load_from_file()
        return cls._instance
