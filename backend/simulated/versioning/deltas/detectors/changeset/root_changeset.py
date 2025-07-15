from simulated.versioning.deltas.detectors.base import ChangeDetector
from simulated.versioning.deltas.detectors.changeset.map import ChangesetMapDetector
from simulated.versioning.deltas.checkpoints.changeset import ChangesetCheckpoint
from typing import Dict, Optional, Any

class ChangesetDetector(ChangeDetector[ChangesetCheckpoint]):
    def __init__(self, map_detector: ChangesetMapDetector):
        self.map_detector = map_detector

    def detect(self, old_checkpoint: ChangesetCheckpoint, new_checkpoint: ChangesetCheckpoint) -> Dict[str, Any] | None:
        """
        The main entry point. It calls the high-level detectors
        and assembles the final 'changes' dictionary.
        """
        changes = {}
        
        map_changes = self.map_detector.detect(old_checkpoint.map_snapshot, new_checkpoint.map_snapshot)
        if map_changes:
            changes["map"] = map_changes

            
        return {"changes": changes} if changes else None