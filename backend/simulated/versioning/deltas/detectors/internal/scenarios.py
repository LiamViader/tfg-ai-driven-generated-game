
from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import ScenarioModel
from typing import List, Dict, Any




class InternalScenarioDetector(ChangeDetector[ScenarioModel]):
    """Aggregates the changes for a single scenario in the report format."""
    def __init__(self, leaf_detectors: list[ChangeDetector[ScenarioModel]]):
        self.leaf_detectors = leaf_detectors

    def detect(self, old_s: ScenarioModel, new_s: ScenarioModel) -> dict[str, Any]:
        # Calls the leaf detectors and merges their results
        aggregated_changes = {}
        for detector in self.leaf_detectors:
            changes = detector.detect(old_s, new_s)
            if changes:
                aggregated_changes.update(changes)
        return aggregated_changes
    
