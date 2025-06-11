from typing import Dict, List, Optional, Literal, Any, Set
from pydantic import BaseModel, Field
from core_game.time.schemas import GameTimeModel
from core_game.map.schemas import ScenarioModel, GameMapModel
from core_game.character.schemas import CharacterBaseModel, PlayerCharacterModel, CharacterRelationship, RelationshipType
from core_game.narrative.schemas import NarrativeStateModel
from core_game.game_event.schemas import GameEventModel

class GameSessionModel(BaseModel):
    """Contains global information and configuration for the game session."""
    session_id: str = Field(..., description="Unique identifier for the game session.")
    player_prompt: str = Field(..., description="The initial prompt that generated this world.")
    narrative_time: GameTimeModel = Field(..., description="The current state of in-game time.")
    global_flags: Dict[str, Any] = Field(default_factory=dict, description="Dictionary for global world state flags (e.g., 'current_weather': 'storm', 'city_on_lockdown': True / False, ).")
    #ATRIBUTS DE RESUM DE LA NARRATIVA INICIAL, DEL MON, ETC


class GameStateModel(BaseModel):
    """
    The main data model containing the complete and centralized state
    of a game session at any given moment. It serves as the 'single source of truth' for the entire system.
    """
    session: GameSessionModel = Field(..., description="Global information about the game session.")

    game_map: GameMapModel
    character_registry: Dict[str, CharacterBaseModel] = Field(
        default_factory=dict,
        description="Registry of all characters (player and NPCs), with their ID as the key."
    )

    player_character: PlayerCharacterModel = Field(
        ...,
        description="The player character"
    )
    
    relationship_types: Dict[str, RelationshipType] = Field(
        default_factory=dict,
        description=("Available type of relationships in the game, key is relationshiptype.name")
    )

    # Relationship matrix: Dict[Character_Source_ID, Dict[Character_Target_ID, Dict[relationshiptype.name, CharacterRelationship]]]
    relationships_matrix: Dict[str, Dict[str, Dict[str, CharacterRelationship]]] = Field(
        default_factory=dict,
        description="Models all kind of relationships between 2 characters."
    )

    narrative_state: NarrativeStateModel = Field(
        ...,
        description="The current state of the narrative, goals, and progression."
    )

    game_event_log: List[GameEventModel] = Field(
        default_factory=list,
        description="A chronological log of all events that have occurred."
    )

    #ATRIBUTS QUE GUARDIN RESUMS DEL QUE HA PASSAT FINS ARA