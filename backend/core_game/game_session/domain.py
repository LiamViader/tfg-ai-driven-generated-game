from typing import Dict, List, Any, Optional, Set
import json
from pathlib import Path

from core_game.map.domain import GameMap
from core_game.character.domain import Characters
from core_game.game_session.schemas import GameSessionModel, generate_session_id
from core_game.time.domain import GameTime
from core_game.narrative.schemas import NarrativeStateModel
from core_game.game_event.schemas import GameEventModel
from core_game.relationship.domain import Relationships

class GameSession:
    """Domain wrapper around :class:`GameSessionModel`."""

    def __init__(self, model: Optional[GameSessionModel] = None) -> None:
        self._session_id: str 
        self._user_prompt: Optional[str]
        self._refined_prompt: Optional[str]
        self._time: GameTime 
        self._global_flags: Dict[str, Any] 
        self._player_main_goal: Optional[str]
        if model:
            self._populate_from_model(model)
        else:
            self._session_id = generate_session_id()
            self._user_prompt = None
            self._refined_prompt = None
            self._time = GameTime()
            self._global_flags = {}
            self._player_main_goal = None
    

    def _populate_from_model(self, model: GameSessionModel) -> None:
        """Populate the domain state from a :class:`GameSessionModel`."""
        self._session_id = model.session_id
        self._user_prompt = model.user_prompt
        self._refined_prompt = model.refined_prompt
        self._time = GameTime(model.narrative_time)
        self._global_flags = model.global_flags
        self._player_main_goal = model.player_main_goal

    # ------------------------------------------------------------------
    # Accessor properties
    # ------------------------------------------------------------------

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def user_prompt(self) -> Optional[str]:
        return self._user_prompt

    @property
    def refined_prompt(self) -> Optional[str]:
        return self._refined_prompt

    @property
    def time(self) -> GameTime:
        return self._time

    @property
    def global_flags(self) -> Dict[str, Any]:
        return self._global_flags

    @property
    def player_main_goal(self) -> Optional[str]:
        return self._player_main_goal

    # ------------------------------------------------------------------
    # Modification methods
    # ------------------------------------------------------------------

    def set_user_prompt(self, prompt: str) -> None:
        """Update the original user prompt."""
        self._user_prompt = prompt

    def set_refined_prompt(self, prompt: str) -> None:
        """Update the refined user prompt."""
        self._refined_prompt = prompt

    def set_player_main_goal(self, goal: str) -> None:
        """Set the player's main goal for the session."""
        self._player_main_goal = goal

    def set_global_flag(self, key: str, value: Any) -> None:
        """Set or update a global flag."""
        self._global_flags[key] = value

    def remove_global_flag(self, key: str) -> None:
        """Remove a global flag, raising KeyError if it doesn't exist."""
        if key in self._global_flags:
            del self._global_flags[key]
        else:
            raise KeyError(f"Global flag '{key}' not found.")

    def advance_time(self, minutes: int) -> None:
        """Advance the in-game time."""
        self._time.advance(minutes)
    