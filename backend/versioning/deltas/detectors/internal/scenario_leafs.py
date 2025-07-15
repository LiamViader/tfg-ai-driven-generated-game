
from versioning.deltas.detectors.base import ChangeDetector
from core_game.map.schemas import GameMapModel
from versioning.deltas.schemas import ChangeDetailModel, ConnectionDiffModel
from core_game.map.schemas import ScenarioModel
from typing import List, Dict, Any


class InternalScenarioVisualsDetector(ChangeDetector[ScenarioModel]):
    """Checks if visual info has changed."""
    def detect(self, old_s: ScenarioModel, new_s: ScenarioModel) -> dict | None:
        visual_attributes = ["visual_description", "type", "zone", "indoor_or_outdoor"]
        visual_changes = {}
        for attr in visual_attributes:
            if getattr(old_s, attr) != getattr(new_s, attr):
                visual_changes[attr] = ChangeDetailModel(old=getattr(old_s, attr), new=getattr(new_s, attr))
        return {"modified_visual_info": visual_changes} if visual_changes else None

class InternalConnectionsDetector(ChangeDetector[ScenarioModel]):
    """Checks if connections has changed"""
    def detect(self, old_s: ScenarioModel, new_s: ScenarioModel) -> dict | None:
        if old_s.connections != new_s.connections:
            # The logic from your old _diff_connections method goes here
            conn_diff = self._diff_connections_logic(old_s.connections, new_s.connections)
            return {"modified_connections": ConnectionDiffModel(**conn_diff)}
        return None
    
    def _diff_connections_logic(self, old_conn: Dict[Any, Any], new_conn: Dict[Any, Any]) -> Dict[str, Any]:
        result = {"added": {}, "removed": {}, "changed": {}}
        keys = set(old_conn.keys()) | set(new_conn.keys())
        for key in keys:
            o = old_conn.get(key)
            n = new_conn.get(key)
            if o == n:
                continue
            if o is None:
                result["added"][key] = n
            elif n is None:
                result["removed"][key] = o
            else:
                result["changed"][key] = {"old": o, "new": n}
        if not any(result.values()):
            return {}
        return result