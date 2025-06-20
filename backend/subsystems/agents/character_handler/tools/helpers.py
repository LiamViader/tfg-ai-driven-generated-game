from typing import Dict, Any


def get_log_item(tool_name: str, success: bool, message: str) -> Dict[str, Any]:
    """Create a log entry for an operation."""
    return {
        "tool_called": tool_name,
        "success": success,
        "message": message,
    }


def get_observation(n_characters: int, tool_name: str, success: bool, message: str) -> str:
    """Generate a standardized observation string."""
    result = "" if success else "Error,"
    observation = (
        f"Result of '{tool_name}': {result} {message} \nCast has {n_characters} characters now."
    )
    print(observation)
    return observation
