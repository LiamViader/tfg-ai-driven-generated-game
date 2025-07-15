from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import ScenarioModel
from typing import List, Dict, Any

class ScenarioNameDetector(ChangeDetector):
    def detect(self, old_scenario: ScenarioModel, new_scenario: ScenarioModel) -> Dict[str, Any] | None:
        if old_scenario.name != new_scenario.name:
            return {"name": new_scenario.name}
        return None

class ScenarioVisualsDetector(ChangeDetector):
    def detect(self, old_scenario: ScenarioModel, new_scenario: ScenarioModel) -> Dict[str, Any] | None:
        if old_scenario.visual_description != new_scenario.visual_description:
            return {"visual_description": new_scenario.visual_description}
        return None
    
class ScenarioDetector(ChangeDetector):
    def __init__(self, leaf_detectors: List[ChangeDetector]):
        self.leaf_detectors: List[ChangeDetector] = leaf_detectors

    def detect(self, old_scenario: ScenarioModel, new_scenario: ScenarioModel) -> Dict[str, Any] | None:
        """
        Calls all of its leaf detectors and aggregates the results into a
        single change dictionary for this scenario.
        """
        full_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old_scenario, new_scenario)
            if changes:
                full_changes.update(changes)
        
        return full_changes if full_changes else None