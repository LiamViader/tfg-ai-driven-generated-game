from typing import Dict, List, Any, Optional
import json
from pathlib import Path

from core_game.map.domain import GameMap
from core_game.character.domain import Characters, Relationships
from core_game.game.schemas import GameStateModel, GameSessionModel
from core_game.time.domain import GameTime


class GameSession:
    """Domain wrapper around :class:`GameSessionModel`."""

    def __init__(self, model: GameSessionModel) -> None:
        self._data = model
        self.session_id: str = model.session_id
        self.player_prompt: str = model.player_prompt
        self.time: GameTime = GameTime(model.narrative_time)
        self.global_flags: Dict[str, Any] = model.global_flags




class GameState:
    def __init__(self, game_state_model: Optional[GameStateModel] = None) -> None:
        """Instantiate the domain game state from its data model."""

        self._data: Optional[GameStateModel] = None
        self.session: Optional[GameSession] = None
        self.game_map: Optional[GameMap] = None
        self.characters: Optional[Characters] = None
        self.relationships: Optional[Relationships] = None
        self.narrative_state = None
        self.game_event_log: List = []

        if game_state_model is not None:
            self._populate_from_model(game_state_model)

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------
    def _populate_from_model(self, game_state_model: GameStateModel) -> None:
        """Populate the domain state from a :class:`GameStateModel`."""

        self._data = game_state_model

        # Session information
        self.session: GameSession = GameSession(game_state_model.session)

        # World map
        self.game_map: GameMap = GameMap(game_state_model.game_map)

        # Characters
        self.characters = Characters(
            game_state_model.character_registry,
            game_state_model.player_character,
        )

        # Relationships
        self.relationships = Relationships(
            game_state_model.relationship_types,
            game_state_model.relationships_matrix,
        )

        # Narrative state
        self.narrative_state = game_state_model.narrative_state

        # Event log
        self.game_event_log: List = game_state_model.game_event_log

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def load_from_file(self, file_path: str = "game_state.json") -> None:
        """Load game state data from a JSON file."""

        if not Path(file_path).is_file():
            raise FileNotFoundError(file_path)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        model = GameStateModel(**data)
        self._populate_from_model(model)

