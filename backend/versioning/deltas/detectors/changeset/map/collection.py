from typing import Dict, Any, List

from core_game.map.schemas import GameMapModel, ConnectionModel
from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.changeset.map.entity import ScenarioDetector
from versioning.deltas.detectors.field_detector import FieldChangeDetector


# --- Helper function to avoid duplicating code ---

def _process_collection(
    old_items: Dict[str, Any], 
    new_items: Dict[str, Any], 
    entity_detector: ChangeDetector
) -> List[Dict[str, Any]]:
    """
    Generic function to process a collection (dict), finding
    add, remove, and update operations.
    """
    ops = []
    old_ids, new_ids = set(old_items), set(new_items)
    
    # Added items
    for id in sorted(new_ids - old_ids):
        ops.append({"op": "add", "id": id, **new_items[id].model_dump()})
    
    # Removed items
    for id in sorted(old_ids - new_ids):
        ops.append({"op": "remove", "id": id})
        
    # Modified items
    for id in sorted(old_ids & new_ids):
        if old_items[id].model_dump() == new_items[id].model_dump():
            continue
            
        entity_changes = entity_detector.detect(old_items[id], new_items[id])
        if entity_changes:
            ops.append({"op": "update", "id": id, **entity_changes})
            
    return ops

# --- Simple detector for an individual Connection ---

class _ConnectionDetector(ChangeDetector[ConnectionModel]):
    """A simple detector for ConnectionModel, as it has no complex sub-models."""
    def __init__(self):
        # We create a field detector for each attribute of ConnectionModel (except 'id').
        self.field_detectors = [
            FieldChangeDetector(field) 
            for field in ConnectionModel.model_fields.keys() if field != 'id'
        ]

    def detect(self, old: ConnectionModel, new: ConnectionModel) -> Dict[str, Any] | None:
        full_changes = {}
        for detector in self.field_detectors:
            changes = detector.detect(old, new)
            if changes:
                full_changes.update(changes)
        return full_changes if full_changes else None

# --- The Main Detector for the Map Collection ---

class MapDetector(ChangeDetector[GameMapModel]):
    """Detects changes in the entire GameMap, including scenarios and connections."""
    def __init__(self, scenario_detector: ScenarioDetector):
        self.scenario_detector = scenario_detector
        self.connection_detector = _ConnectionDetector()

    def detect(self, old: GameMapModel, new: GameMapModel) -> Dict[str, Any] | None:
        final_changes = {}

        # 1. Process the scenarios collection using the helper and its specific detector
        scenario_ops = _process_collection(
            old_items=old.scenarios, 
            new_items=new.scenarios, 
            entity_detector=self.scenario_detector
        )
        if scenario_ops:
            final_changes["scenarios"] = scenario_ops

        # 2. Process the connections collection using the helper and its specific detector
        connection_ops = _process_collection(
            old_items=old.connections, 
            new_items=new.connections, 
            entity_detector=self.connection_detector
        )
        if connection_ops:
            final_changes["connections"] = connection_ops
            
        return final_changes if final_changes else None