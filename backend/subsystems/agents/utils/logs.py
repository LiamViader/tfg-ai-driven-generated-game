from typing import Dict, Any
from subsystems.agents.utils.schemas import ToolLog


def get_log_item(tool_name: str, args: Dict[str,Any], is_query: bool, success: bool, message: str) -> ToolLog:
    """Helper to log the operation and create consistent observation messages."""
    return ToolLog(tool_called=tool_name, args=args, is_query=is_query, success=success, message=message)

def extract_tool_args(locals_dict: Dict[str, Any]) -> Dict[str, Any]:
    exclude_keys = {"logs_field_to_update", "messages_field_to_update", "tool_call_id"}
    return {k: v for k, v in locals_dict.items() if k not in exclude_keys}