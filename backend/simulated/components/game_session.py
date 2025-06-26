from copy import deepcopy
from typing import Any, Optional

from core_game.game_session.domain import GameSession


class SimulatedGameSession:
    """Lightweight wrapper around :class:`GameSession` for isolated modifications."""

    def __init__(self, session: GameSession) -> None:
        self._working_state: GameSession = session

    def __deepcopy__(self, memo):
        copied_session = deepcopy(self._working_state)
        return SimulatedGameSession(session=copied_session)

    def get_state(self) -> GameSession:
        return self._working_state

    # ----- Modification methods -----
    def set_user_prompt(self, prompt: str) -> None:
        self._working_state.set_user_prompt(prompt)

    def set_refined_prompt(self, prompt: str) -> None:
        self._working_state.set_refined_prompt(prompt)

    def set_player_main_goal(self, goal: str) -> None:
        self._working_state.set_player_main_goal(goal)

    def set_global_flag(self, key: str, value: Any) -> None:
        self._working_state.set_global_flag(key, value)

    def remove_global_flag(self, key: str) -> None:
        self._working_state.remove_global_flag(key)

    def advance_time(self, minutes: int) -> None:
        self._working_state.advance_time(minutes)

    # ----- Read methods -----
    def get_user_prompt(self) -> Optional[str]:
        return self._working_state.user_prompt

    def get_refined_prompt(self) -> Optional[str]:
        return self._working_state.refined_prompt


    def get_player_main_goal(self) -> Optional[str]:
        return self._working_state.player_main_goal


    def get_global_flags(self) -> dict[str, Any]:
        return dict(self._working_state.global_flags)

    def get_time(self):
        return self._working_state.time
