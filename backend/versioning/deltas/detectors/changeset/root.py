from typing import Dict, Any

from versioning.deltas.checkpoints.changeset import ChangesetCheckpoint
from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.changeset.map.collection import MapDetector
from versioning.deltas.detectors.changeset.characters.collection import CharactersDetector
from versioning.deltas.detectors.changeset.game_events.collection import GameEventsDetector # ¡Nuevo import!

class ChangesetDetector(ChangeDetector[ChangesetCheckpoint]):
    """
    The root detector that orchestrates all high-level domain detectors
    (map, characters, events, etc.) to build the final, complete changeset.
    """
    def __init__(
        self,
        map_detector: MapDetector,
        characters_detector: CharactersDetector,
        game_events_detector: GameEventsDetector, # ¡Añadimos el events_detector aquí!
    ):
        self.map_detector = map_detector
        self.characters_detector = characters_detector
        self.game_events_detector = game_events_detector # ¡Lo asignamos!

    def detect(self, old_cp: ChangesetCheckpoint, new_cp: ChangesetCheckpoint) -> Dict[str, Any] | None:
        """
        Calls each domain detector and assembles their results into the
        final 'changes' dictionary.
        """
        changes: Dict[str, Any] = {}
        # 1. Detectar cambios en el mapa
        map_changes = self.map_detector.detect(old_cp.map_snapshot, new_cp.map_snapshot)
        if map_changes:
            
            changes["map"] = map_changes

        print("Detecting changes in rooot")
        # 2. Detectar cambios en los personajes
        char_changes = self.characters_detector.detect(old_cp.characters_snapshot, new_cp.characters_snapshot)
        if char_changes:
            print("Changes detected in characters")
            changes["characters"] = char_changes

        # 3. Detectar cambios en los eventos (opciones de interacción de personajes)
        # El EventsDetector ya opera sobre los modelos (GameEventsManagerModel)
        events_changes = self.game_events_detector.detect(old_cp.game_events_snapshot, new_cp.game_events_snapshot)
        if events_changes:
            changes["events"] = events_changes # La clave en el changeset será "events" o "interactions"

        # Devolvemos el diccionario de cambios solo si hay alguno
        return {"changes": changes} if changes else None