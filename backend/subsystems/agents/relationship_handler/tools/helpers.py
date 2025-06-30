from typing import Dict, Any


def get_observation(n_relationships: int, tool_name: str, success: bool, message: str) -> str:
    """Generate a standardized observation string."""
    result = "" if success else "Error,"
    observation = (
        f"Result of '{tool_name}': {result} {message} \nRelationships count: {n_relationships}."
    )
    print(observation)
    return observation
