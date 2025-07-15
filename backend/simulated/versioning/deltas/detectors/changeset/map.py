from simulated.versioning.deltas.detectors.changeset.scenarios import ChangesetScenarioDetector
from simulated.versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import GameMapModel
from typing import Dict, Any

class ChangesetMapDetector(ChangeDetector[GameMapModel]):
    def __init__(self, scenario_detector: ChangesetScenarioDetector):
        self.scenario_detector = scenario_detector

    def detect(self, old_map: GameMapModel, new_map: GameMapModel) -> Dict[str, Any] | None:
        """
        Compares two maps, finds the changes in scenarios, and uses
        the ScenarioDetector to get the details for each one.
        """
        ops = []
        old_scenarios, new_scenarios = old_map.scenarios, new_map.scenarios
        old_ids, new_ids = set(old_scenarios), set(new_scenarios)

        for id in sorted(new_ids - old_ids):
            ops.append({"op": "add", "id": id, **new_scenarios[id].model_dump()})
        
        for id in sorted(old_ids - new_ids):
            ops.append({"op": "remove", "id": id})
            
        for id in sorted(old_ids & new_ids):
            # Call the child detector to see if this scenario has changed
            scenario_changes = self.scenario_detector.detect(old_scenarios[id], new_scenarios[id])
            if scenario_changes:
                ops.append({"op": "update", "id": id, **scenario_changes})
        
        return {"scenarios": ops} if ops else None
    

