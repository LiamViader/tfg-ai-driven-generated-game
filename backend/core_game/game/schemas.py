from typing import Dict, List, Optional, Literal, Any, Set
from pydantic import BaseModel, Field
from core_game.time.schemas import GameTimeModel
from core_game.map.schemas import ScenarioModel, GameMapModel
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel, CharactersModel
from core_game.narrative.schemas import NarrativeStateModel
from core_game.game_event.schemas import GameEventModel
from core_game.relationship.schemas import RelationshipsModel

_session_id_counter = 0


def generate_session_id() -> str:
    """Return a sequential id of the form 'scenario_001'."""
    global _session_id_counter
    _session_id_counter += 1
    return f"session_{_session_id_counter:03d}"

class GameSessionModel(BaseModel):
    """Contains global information and configuration for the game session."""
    session_id: str = Field(..., description="Unique identifier for the game session.")
    user_prompt: str = Field(..., description="The initial prompt that generated this world.")
    refined_prompt: str = Field(..., description="The refined user prompt")
    player_main_goal: str = Field(..., description="The main goal for the player in the narrative")
    narrative_time: GameTimeModel = Field(..., description="The current state of in-game time.")
    global_flags: Dict[str, Any] = Field(default_factory=dict, description="Dictionary for global world state flags (e.g., 'current_weather': 'storm', 'city_on_lockdown': True / False, ).")


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