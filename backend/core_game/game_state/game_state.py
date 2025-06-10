from core_game.map.schemas import ScenarioModel
from core_game.map.map import Map
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel
from typing import Dict


class GameSession:
    def __init__(self):
        self.map: Map = Map()
        self.time: float = 0.0
        self.characters: Dict[str, CharacterBaseModel] = {}
        self.player: PlayerCharacterModel
