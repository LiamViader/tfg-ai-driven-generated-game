from core_game.map.schemas import ScenarioModel
from core_game.character.schemas import CharacterBase, PlayerCharacter
from typing import Dict


class GameSession:
    def __init__(self):
        self.map: Dict[str, ScenarioModel] = {}
        self.time: float = 0.0
        self.characters: Dict[str, CharacterBase] = {}
        self.player: PlayerCharacter

    def advance_time(self, amount: float):
        self.time += amount