from core_game.map.schemas import ScenarioModel
from typing import Dict

class Map():
    def __init__(self):
        self.map: Dict[str, ScenarioModel] = {}