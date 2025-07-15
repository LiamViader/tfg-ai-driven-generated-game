from simulated.versioning.deltas.schemas import DiffResultModel
from simulated.versioning.deltas.detectors.base import ChangeDetector
from simulated.versioning.deltas.checkpoints.internal import InternalStateCheckpoint
from simulated.versioning.deltas.detectors.internal.map import InternalMapDetector
from simulated.versioning.deltas.detectors.internal.characters import InternalCharactersCollectionDetector

class InternalDiffDetector(ChangeDetector[InternalStateCheckpoint]):
    """
    Top-level detector for the internal diffing system...
    """
    # Cambia el tipo del segundo argumento aquí
    def __init__(self, map_detector: InternalMapDetector, character_detector: InternalCharactersCollectionDetector):
        self.map_detector = map_detector
        self.character_detector = character_detector

    def detect(self, old_cp: InternalStateCheckpoint, new_cp: InternalStateCheckpoint) -> DiffResultModel:
        scenario_diff = self.map_detector.detect(old_cp.map_snapshot, new_cp.map_snapshot)
        # Ahora esta llamada es correcta según el tipado
        character_diff = self.character_detector.detect(old_cp.characters_snapshot, new_cp.characters_snapshot)
        
        return DiffResultModel(scenarios=scenario_diff, characters=character_diff)