from .manager import StateCheckpointManager
from simulated.game_state import SimulatedGameState

# Importa todas las piezas necesarias para construir los árboles
from simulated.versioning.deltas.detectors.changeset.root_changeset import ChangesetDetector
from simulated.versioning.deltas.detectors.changeset.map import ChangesetMapDetector
from simulated.versioning.deltas.detectors.changeset.scenarios import ChangesetScenarioDetector
from simulated.versioning.deltas.detectors.changeset.scenario_leafs import ScenarioNameDetector, ScenarioVisualsDetector
from simulated.versioning.deltas.detectors.internal.root_internal import InternalDiffDetector
from simulated.versioning.deltas.detectors.internal.map import InternalMapDetector
from simulated.versioning.deltas.detectors.internal.scenarios import InternalScenarioDetector
from simulated.versioning.deltas.detectors.internal.scenario_leafs import InternalScenarioVisualsDetector, InternalConnectionsDetector
from simulated.versioning.deltas.detectors.internal.characters import InternalCharacterDetector, InternalCharactersCollectionDetector
from simulated.versioning.deltas.detectors.internal.character_leafs import InternalCharacterVisualsDetector, InternalCharacterLocationDetector
class CheckpointManagerFactory:
    """
    Its only job is to create fully configured instances
    of StateCheckpointManager with default detector trees.
    """
    def create_manager(self, state: SimulatedGameState) -> StateCheckpointManager:
        # --- 1. Construir el árbol de detectores para Changeset ---
        changeset_scenario_detector = ChangesetScenarioDetector(
            leaf_detectors=[
                ScenarioNameDetector(), 
                ScenarioVisualsDetector()
            ]
        )
        changeset_map_detector = ChangesetMapDetector(
            scenario_detector=changeset_scenario_detector
        )
        # ... (aquí construirías el de personajes) ...
        default_changeset_detector = ChangesetDetector(
            map_detector=changeset_map_detector,
        )

        # --- 2. Construir el árbol de detectores para Diff Interno ---
        internal_scenario_detector = InternalScenarioDetector(
            leaf_detectors=[
                InternalScenarioVisualsDetector(), 
                InternalConnectionsDetector()
            ]
        )
        internal_map_detector = InternalMapDetector(
            scenario_detector=internal_scenario_detector
        )
        internal_character_leafs = [
            InternalCharacterVisualsDetector(), 
            InternalCharacterLocationDetector()
        ]
        internal_character_detector = InternalCharacterDetector(leaf_detectors=internal_character_leafs)
        internal_chars_collection_detector = InternalCharactersCollectionDetector(
            character_detector=internal_character_detector
        )
        default_internal_diff_detector = InternalDiffDetector(
            map_detector=internal_map_detector,
            character_detector=internal_chars_collection_detector
        )

        # --- 3. Crear y devolver el Manager con todo inyectado ---
        manager = StateCheckpointManager(
            state=state,
            default_changeset_detector=default_changeset_detector,
            default_internal_diff_detector=default_internal_diff_detector
        )
        return manager