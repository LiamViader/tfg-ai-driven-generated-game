from typing import Dict, List, Any, Optional, Set
import json
from pathlib import Path

from core_game.map.domain import GameMap
from core_game.character.domain import Characters
from core_game.game_state.schemas import GameStateModel
from core_game.time.domain import GameTime
from core_game.narrative.domain import NarrativeState
from core_game.game_event.schemas import GameEventModel
from core_game.relationship.domain import Relationships
from core_game.game_session.domain import GameSession

class GameState:
    def __init__(self, game_state_model: Optional[GameStateModel] = None) -> None:
        """Instantiate the domain game state from its data model."""

        self._session: GameSession
        self._game_map: GameMap
        self._characters: Characters
        self._relationships: Relationships
        self._narrative_state: NarrativeState
        self._game_event_log: List[GameEventModel]

        if game_state_model is not None:
            self._populate_from_model(game_state_model)
        else:
            self._session = GameSession()
            self._game_map = GameMap()
            self._characters = Characters()
            self._relationships = Relationships()
            self._narrative_state = NarrativeState()
            self._game_event_log = []


    @property
    def session(self) -> GameSession:
        return self._session

    @property
    def game_map(self) -> GameMap:
        return self._game_map
    
    @property
    def characters(self) -> Characters:
        return self._characters

    @property
    def relationships(self) -> Relationships:
        return self._relationships

    @property
    def narrative_state(self) -> NarrativeState:
        return self._narrative_state


    def _populate_from_model(self, game_state_model: GameStateModel) -> None:
        """Populate the domain state from a :class:`GameStateModel`."""

        self._session = GameSession(game_state_model.session)
        self._game_map = GameMap(game_state_model.game_map)
        self._characters = Characters(game_state_model.characters)
        self._relationships = Relationships(game_state_model.relationships)
        self._narrative_state = NarrativeState(game_state_model.narrative_state)
        self._game_event_log = game_state_model.game_event_log

    def load_from_file(self, file_path: str = "game_state.json") -> None:
        """Load game state data from a JSON file."""

        if not Path(file_path).is_file():
            raise FileNotFoundError(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        model = GameStateModel(**data)
        self._populate_from_model(model)

    def update_characters(self, characters: Characters) -> None:
        self._characters = characters
    
    def update_map(self, map: GameMap) -> None:
        self._game_map = map

    def update_session(self, session: GameSession) -> None:
        """Update the game session component."""
        self._session = session

    def update_relationships(self, relationships: Relationships) -> None:
        self._relationships = relationships

    def update_narrative_state(self, narrative_state: NarrativeState) -> None:
        self._narrative_state = narrative_state





