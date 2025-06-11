from core_game.map.schemas import ScenarioModel, ScenarioSnapshot
from typing import Dict

class Scenario:
    def __init__(self, scenario_model: ScenarioModel):
        self._data: ScenarioModel = scenario_model
    
    @property
    def id(self) -> str:
        return self._data.id
        
    @property
    def name(self) -> str:
        return self._data.name
    
    def snapshot_scenario(self, current_time: float):
        snapshot = ScenarioSnapshot(
            name=self._data.name,
            visual_description=self._data.visual_description,
            narrative_context=self._data.narrative_context,
            summary_description=self._data.summary_description,
            indoor_or_outdoor=self._data.indoor_or_outdoor,
            type=self._data.type,
            zone=self._data.zone,
            connections=self._data.connections.copy(),
            valid_from=self._data.valid_from,
            valid_until=current_time
        )
        self._data.valid_from = current_time
        self._data.previous_versions.append(snapshot)


class GameMap():
    def __init__(self, game_map: Dict[str, Scenario]):
        self.map: Dict[str, Scenario] = game_map