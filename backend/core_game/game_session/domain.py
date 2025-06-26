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
    