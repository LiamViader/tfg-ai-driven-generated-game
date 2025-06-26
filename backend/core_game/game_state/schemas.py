from typing import Dict, List, Optional, Literal, Any, Set
from pydantic import BaseModel, Field
from core_game.time.schemas import GameTimeModel
from core_game.map.schemas import ScenarioModel, GameMapModel
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel, CharactersModel
from core_game.narrative.schemas import NarrativeStateModel
from core_game.game_event.schemas import GameEventModel
from core_game.relationship.schemas import RelationshipsModel
from core_game.game_session.schemas import GameSessionModel

class GameStateModel(BaseModel):
    """
    The main data model containing the complete and centralized state
    of a game session at any given moment. It serves as the 'single source of truth' for the entire system.
    """
    session: GameSessionModel = Field(..., description="Global information about the game session.")

    game_map: GameMapModel = Field(..., description="Map model component")

    characters: CharactersModel = Field(..., description="Characters model component")
    
    relationships: RelationshipsModel = Field(..., description="Relationships model component")

    narrative_state: NarrativeStateModel = Field(
        ...,
        description="The current state of the narrative, goals, and progression."
    )

    game_event_log: List[GameEventModel] = Field(
        default_factory=list,
        description="A chronological log of all events that have occurred."
    )

    #ATRIBUTS QUE GUARDIN RESUMS DEL QUE HA PASSAT FINS ARA