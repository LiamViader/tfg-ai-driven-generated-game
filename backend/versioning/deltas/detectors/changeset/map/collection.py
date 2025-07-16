from typing import Dict, Any, List

from core_game.map.schemas import GameMapModel, ConnectionModel
from versioning.deltas.detectors.base import ChangeDetector
from versioning.deltas.detectors.changeset.map.entity import ScenarioDetector, ConnectionInfoDetector
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
        model = new_items[id]
        dumped = model.model_dump()

        # Convert connections dict to list of ScenarioConnectionChange ops
        if "connections" in dumped and isinstance(dumped["connections"], dict):
            dumped["connections"] = [
                {"op": "add", "direction": direction, "value": conn_id}
                for direction, conn_id in dumped["connections"].items()
                if conn_id is not None
            ]

        ops.append({"op": "add", "id": id, **dumped})
    
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


# --- The Main Detector for the Map Collection ---

class MapDetector(ChangeDetector[GameMapModel]):
    """Detects changes in the entire GameMap, including scenarios and connections."""
    def __init__(self, scenario_detector: ScenarioDetector, connection_detector: ConnectionInfoDetector):
        self.scenario_detector = scenario_detector
        self.connection_detector = connection_detector

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