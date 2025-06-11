from core_game.map.schemas import ScenarioModel
from core_game.map.domain import GameMap, Scenario
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel
from core_game.game.schemas import GameStateModel
from typing import Dict


class GameState:
    def __init__(self, game_state_model: GameStateModel):
        self.game_map: GameMap = GameMap(game_state_model.game_map)

