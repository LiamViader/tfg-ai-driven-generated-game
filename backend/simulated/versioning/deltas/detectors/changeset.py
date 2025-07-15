from simulated.versioning.deltas.detectors.base import ChangeDetector
from simulated.versioning.deltas.detectors.map import MapDetector
from simulated.versioning.deltas.checkpoints.changeset import ChangesetCheckpoint
from simulated.versioning.deltas.detectors.scenarios import *

class ChangesetDetector(ChangeDetector):
    def __init__(self):
        self.map_detector = MapDetector(ScenarioDetector(
            [
                ScenarioNameDetector(),
                ScenarioVisualsDetector(),
            ]
        ))

    def detect(self, old_checkpoint: ChangesetCheckpoint, new_checkpoint: ChangesetCheckpoint) -> dict | None:
        """
        The main entry point. It calls the high-level detectors
        and assembles the final 'changes' dictionary.
        """
        changes = {}
        
        map_changes = self.map_detector.detect(old_checkpoint.map_snapshot, new_checkpoint.map_snapshot)
        if map_changes:
            changes["map"] = map_changes

            
        return {"changes": changes} if changes else None