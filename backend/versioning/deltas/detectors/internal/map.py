
from versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import GameMapModel
from versioning.deltas.schemas import ScenarioDiffModel
from versioning.deltas.detectors.internal.scenarios import InternalScenarioDetector
class InternalMapDetector(ChangeDetector[GameMapModel]):
    """Replicates the logic of `diff_scenarios_against`, returning a ScenarioDiffModel."""
    def __init__(self, scenario_detector: InternalScenarioDetector):
        self.scenario_detector = scenario_detector

    def detect(self, old_map: GameMapModel, new_map: GameMapModel) -> ScenarioDiffModel:
        old_scenarios, new_scenarios = old_map.scenarios, new_map.scenarios
        old_ids, new_ids = set(old_scenarios), set(new_scenarios)
        
        diff_dict = {
            "added": sorted(list(new_ids - old_ids)),
            "removed": sorted(list(old_ids - new_ids)),
            "modified": [],
            "modified_visual_info": {},
            "modified_connections": {},
        }

        for id in sorted(old_ids & new_ids):
            if old_scenarios[id].model_dump() == new_scenarios[id].model_dump():
                continue

            diff_dict["modified"].append(id)
            details = self.scenario_detector.detect(old_scenarios[id], new_scenarios[id])
            if details:
                if "modified_visual_info" in details:
                    diff_dict["modified_visual_info"][id] = details["modified_visual_info"]
                if "modified_connections" in details:
                    diff_dict["modified_connections"][id] = details["modified_connections"]
        
        return ScenarioDiffModel(**diff_dict)