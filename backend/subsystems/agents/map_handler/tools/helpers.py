from typing import Dict, List, Any, Optional, Set



from core_game.map.schemas import  ScenarioModel


def get_log_item(tool_name: str, success: bool, message: str) -> Dict[str, Any]:
        """Helper to log the operation and create consistent observation messages."""

        return {
            "tool_called": tool_name,
            "success": success,
            "message": message
        }

def get_observation(n_scenarios:int, tool_name: str, success:bool, message: str) -> str:
        """Helper to log the operation and create consistent observation messages."""
        result = "" if success else "Error,"
        observation = f"Result of '{tool_name}': {result} {message} \nMap has {n_scenarios} scenarios now."
        print(observation)
        return observation



