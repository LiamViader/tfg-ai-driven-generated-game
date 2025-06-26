from typing import Dict, Any, List, Union
from subsystems.agents.utils.schemas import ToolLog, ClearLogs


def get_log_item(tool_name: str, args: Dict[str,Any], is_query: bool, success: bool, message: str) -> ToolLog:
    """Helper to log the operation and create consistent observation messages."""
    return ToolLog(tool_called=tool_name, args=args, is_query=is_query, success=success, message=message)

def extract_tool_args(locals_dict: Dict[str, Any]) -> Dict[str, Any]:
    exclude_keys = {"logs_field_to_update", "messages_field_to_update", "tool_call_id"}
    return {k: v for k, v in locals_dict.items() if k not in exclude_keys}


def log_reducer(existing_logs: List[ToolLog], new_value: Union[List[ToolLog], ClearLogs, None]) -> List[ToolLog]:
    """
    Función reductora para los logs.
    - Si el nuevo valor es ClearLogs, borra la lista.
    - Si el nuevo valor es una lista, la añade.
    - Si el nuevo valor es None, no hace nada.
    """
    if isinstance(new_value, ClearLogs):
        # Si recibimos la señal, devolvemos una lista vacía, borrando lo anterior.
        return []
    if isinstance(new_value, list):
        # Si recibimos una lista, la añadimos (comportamiento normal).
        return existing_logs + new_value
    
    # Si el nodo no devuelve nada para esta clave (new_value es None), no cambiamos nada.
    return existing_logs