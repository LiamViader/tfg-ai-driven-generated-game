from typing import Dict, Any, List
from core_game.map.schemas import ScenarioModel
from simulated.versioning.deltas.detectors.base import ChangeDetector

class ScenarioConnectionsDetector(ChangeDetector[ScenarioModel]):
    """
    Detects granular changes within the connections dictionary of a scenario,
    producing add, remove, or update operations for each change.
    """
    def detect(self, old: ScenarioModel, new: ScenarioModel) -> Dict[str, Any] | None:
        if old.connections == new.connections:
            return None

        ops: List[Dict[str, Any]] = []
        old_keys = set(old.connections.keys())
        new_keys = set(new.connections.keys())

        for direction in old_keys:
            old_conn_id = old.connections.get(direction)
            new_conn_id = new.connections.get(direction)

            if direction not in new_keys:
                # Ya no existe la dirección, se asume que la conexión es null/eliminada
                ops.append({"op": "remove", "direction": str(direction)})
            elif old_conn_id != new_conn_id:
                # La conexión en esta dirección ha cambiado
                ops.append({"op": "update", "direction": str(direction), "value": new_conn_id})
        
        # Comprobar conexiones nuevas
        for direction in new_keys - old_keys:
            ops.append({"op": "add", "direction": str(direction), "value": new.connections[direction]})

        return {"connections": ops} if ops else None