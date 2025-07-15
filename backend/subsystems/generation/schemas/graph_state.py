from typing import Dict, List, Optional, Callable
from pydantic import BaseModel, Field, PrivateAttr
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from core_game.narrative.schemas import NarrativeStructureTypeModel
from subsystems.agents.character_handler.schemas.graph_state import CharacterGraphState
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.seed.schemas.graph_state import SeedGenerationGraphState
from utils.progress_tracker import ProgressTracker

class GenerationGraphState(RefinementLoopGraphState, SeedGenerationGraphState):
    initial_state_checkpoint_id: Optional[str] = Field(
        default=None,
        description="The unique ID of the checkpoint created at the start of the generation process."
    )
    generation_progress_tracker: Optional[ProgressTracker] = Field(
        default=None,
    )
    class Config:
        arbitrary_types_allowed = True