from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import ScenarioModel
from typing import List, Dict, Any

class ScenarioNameDetector(ChangeDetector[ScenarioModel]):
    def detect(self, old_scenario: ScenarioModel, new_scenario: ScenarioModel) -> Dict[str, Any] | None:
        if old_scenario.name != new_scenario.name:
            return {"name": new_scenario.name}
        return None

class ScenarioVisualsDetector(ChangeDetector[ScenarioModel]):
    def detect(self, old_scenario: ScenarioModel, new_scenario: ScenarioModel) -> Dict[str, Any] | None:
        if old_scenario.visual_description != new_scenario.visual_description:
            return {"visual_description": new_scenario.visual_description}
        return None