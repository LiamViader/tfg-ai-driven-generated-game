from core_game.game_state.game_state_schema import MapModel

class GameState:
    def __init__(self):
        self.map: MapModel = MapModel()
        self.time: float = 0.0

    def advance_time(self, amount: float):
        self.time += amount