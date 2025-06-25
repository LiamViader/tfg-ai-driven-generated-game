from typing import Dict, List, Optional, Any, Annotated, Sequence
from pydantic import BaseModel, Field
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from core_game.narrative.schemas import NarrativeStructureTypeModel
from subsystems.agents.character_handler.schemas.graph_state import CharacterGraphState
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.seed.schemas.graph_state import SeedGenerationGraphState

class GenerationGraphState(RefinementLoopGraphState, SeedGenerationGraphState):
    pass