def get_observation(tool_name: str, success: bool, message: str) -> str:
    """Generate a standardized observation string for game events."""
    result = "" if success else "Error,"
    observation = f"Result of '{tool_name}': {result} {message}"
    print(observation)
    return observation
