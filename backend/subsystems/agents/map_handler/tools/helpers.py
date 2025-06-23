
def get_observation(n_scenarios:int, tool_name: str, success:bool, message: str) -> str:
        """Helper to log the operation and create consistent observation messages."""
        result = "" if success else "Error,"
        observation = f"Result of '{tool_name}': {result} {message} \nMap has {n_scenarios} scenarios now."
        print(observation)
        return observation



