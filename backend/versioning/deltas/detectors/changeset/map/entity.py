from typing import Dict, Any, List

from core_game.map.schemas import ScenarioModel, ConnectionModel
from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.field_detector import FieldChangeDetector
from versioning.deltas.detectors.changeset.map.attributes import ScenarioConnectionsDetector


class ScenarioDetector(ChangeDetector[ScenarioModel]):
    """
    Aggregates all changes for a single Scenario entity.
    It uses specialized detectors for complex fields like 'connections'.
    """
    def __init__(self):
        """
        Initializes the detector with a list of simple field detectors
        and specialized detectors for complex attributes.
        """
        # 2. La lista ahora solo contiene los campos simples
        self.field_detectors: List[ChangeDetector] = [
            FieldChangeDetector("name"),
            FieldChangeDetector("visual_description"),
            FieldChangeDetector("narrative_context"),
            FieldChangeDetector("summary_description"),
            FieldChangeDetector("indoor_or_outdoor"),
            FieldChangeDetector("type"),
            FieldChangeDetector("zone"),
            FieldChangeDetector("image_path"),
        ]
        # 3. Instanciamos nuestro detector especializado
        self.connections_detector = ScenarioConnectionsDetector()

    def detect(self, old: ScenarioModel, new: ScenarioModel) -> Dict[str, Any] | None:
        """
        Detects changes by delegating to the appropriate detectors
        and aggregates the results.
        """
        full_changes = {}
        for detector in self.field_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)

        connection_changes = self.connections_detector.detect(old, new)
        if connection_changes:
            full_changes.update(connection_changes)

        return full_changes if full_changes else None
    
class ConnectionInfoDetector(ChangeDetector[ConnectionModel]):
    """
    Aggregates all changes for a single Connection entity.
    """
    def __init__(self):
        """
        Initializes the detector with a list of simple field detectors
        """
        # 2. La lista ahora solo contiene los campos simples
        self.field_detectors: List[ChangeDetector] = [
            FieldChangeDetector("name"),
            FieldChangeDetector("scenario_a_id"),
            FieldChangeDetector("scenario_b_id"),
            FieldChangeDetector("direction_from_a"),
            FieldChangeDetector("connection_type"),
            FieldChangeDetector("travel_description"),
            FieldChangeDetector("traversal_conditions"),
            FieldChangeDetector("exit_appearance_description"),
            FieldChangeDetector("is_blocked")
        ]
        # 3. Instanciamos nuestro detector especializado
        self.connections_detector = ScenarioConnectionsDetector()

    def detect(self, old: ConnectionModel, new: ConnectionModel) -> Dict[str, Any] | None:
        """
        Detects changes by delegating to the appropriate detectors
        and aggregates the results.
        """
        full_changes = {}

        for detector in self.field_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)


        return full_changes if full_changes else None