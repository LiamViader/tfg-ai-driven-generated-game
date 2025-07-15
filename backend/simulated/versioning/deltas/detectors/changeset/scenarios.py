from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import ScenarioModel
from typing import List, Dict, Any
    
class ChangesetScenarioDetector(ChangeDetector[ScenarioModel]):
    def __init__(self, leaf_detectors: List[ChangeDetector[ScenarioModel]]):
        self.leaf_detectors: List[ChangeDetector[ScenarioModel]] = leaf_detectors

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