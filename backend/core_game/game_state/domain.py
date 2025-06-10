from core_game.map.schemas import ScenarioModel
from core_game.map.domain import GameMap
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel
from typing import Dict


class GameState:
    def __init__(self):
        self.map: GameMap = GameMap()
        self.time: float = 0.0
        self.characters: Dict[str, CharacterBaseModel] = {}
        self.player: PlayerCharacterModel
