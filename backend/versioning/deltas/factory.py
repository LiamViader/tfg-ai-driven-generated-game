from .manager import StateCheckpointManager
from simulated.game_state import SimulatedGameState

# Importa todas las piezas necesarias para construir los árboles
# --- Imports for the Changeset Detector Tree ---
from versioning.deltas.detectors.changeset.root import ChangesetDetector
from versioning.deltas.detectors.changeset.map.collection import MapDetector as ChangesetMapDetector
from versioning.deltas.detectors.changeset.map.entity import ScenarioDetector as ChangesetScenarioDetector
from versioning.deltas.detectors.changeset.characters.collection import CharactersDetector as ChangesetCharactersDetector
from versioning.deltas.detectors.changeset.characters.entity import CharacterDetector as ChangesetCharacterDetector
# You would also import game_events detector here if you had one

# --- Imports for the Internal Diff Detector Tree ---
from versioning.deltas.detectors.internal.root_internal import InternalDiffDetector
from versioning.deltas.detectors.internal.map import InternalMapDetector
from versioning.deltas.detectors.internal.scenarios import InternalScenarioDetector
from versioning.deltas.detectors.internal.scenario_leafs import InternalScenarioVisualsDetector, InternalConnectionsDetector
from versioning.deltas.detectors.internal.characters import InternalCharacterDetector, InternalCharactersCollectionDetector
from versioning.deltas.detectors.internal.character_leafs import InternalCharacterVisualsDetector, InternalCharacterLocationDetector

class CheckpointManagerFactory:
    """
    Its only job is to create fully configured instances
    of StateCheckpointManager with default detector trees.
    """
    def create_manager(self, state: SimulatedGameState) -> StateCheckpointManager:
        # --- 1. Construct tree for changeset detectors ---
        changeset_scenario_detector = ChangesetScenarioDetector()
        changeset_map_detector = ChangesetMapDetector(
            scenario_detector=changeset_scenario_detector
        )
        
        changeset_character_detector = ChangesetCharacterDetector()
        changeset_characters_collection_detector = ChangesetCharactersDetector(
            character_detector=changeset_character_detector
        )

        default_changeset_detector = ChangesetDetector(
            map_detector=changeset_map_detector,
            characters_detector=changeset_characters_collection_detector
        )

        # --- 2. Construct tree for internal diffs ---
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

        # --- 3. Create and return manager ---
        manager = StateCheckpointManager(
            state=state,
            default_changeset_detector=default_changeset_detector,
            default_internal_diff_detector=default_internal_diff_detector
        )
        return manager