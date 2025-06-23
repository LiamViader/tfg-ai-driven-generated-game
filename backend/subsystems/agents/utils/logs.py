from typing import Dict, Any
from subsystems.agents.utils.schemas import ToolLog


def get_log_item(tool_name: str, args: Dict[str,Any], is_query: bool, success: bool, message: str) -> ToolLog:
    """Helper to log the operation and create consistent observation messages."""
    return ToolLog(tool_called=tool_name, args=args, is_query=is_query, success=success, message=message)