from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from core_game.narrative.structures import AVAILABLE_NARRATIVE_STRUCTURES
from subsystems.generation.schemas.graph_state import GenerationGraphState

# Helper mapping from id to structure
AVAILABLE_STRUCTURES_BY_ID = {s.id: s for s in AVAILABLE_NARRATIVE_STRUCTURES}

class ToolSelectStructureArgs(BaseModel):
    structure_id: str = Field(..., description="ID of the narrative structure to select")
    state: Annotated[GenerationGraphState, InjectedState()]  # entire state injection

class ToolGetStructureInfoArgs(BaseModel):
    structure_id: str = Field(..., description="ID of the structure")

@tool(args_schema=ToolSelectStructureArgs)
def select_narrative_structure(structure_id: str, state: Annotated[GenerationGraphState, InjectedState()]) -> str:
    """Select one of the available narrative structures by its id."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return f"Structure id '{structure_id}' not found"
    state.selected_structure_type_id = struct.id
    state.selected_structure_type_name = struct.name
    return f"Selected narrative structure '{struct.name}'"

@tool(args_schema=ToolGetStructureInfoArgs)
def get_structure_description(structure_id: str) -> str:
    """Get description and use cases of a narrative structure."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return f"Structure id '{structure_id}' not found"
    return f"{struct.name}: {struct.description} Use cases: {struct.orientative_use_cases}"

@tool(args_schema=ToolGetStructureInfoArgs)
def get_structure_stages(structure_id: str) -> str:
    """List the stages of the given structure."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return f"Structure id '{structure_id}' not found"
    return "\n".join([f"{i+1}. {stage.name}: {stage.narrative_objectives}" for i, stage in enumerate(struct.stages)])

STRUCTURE_TOOLS = [select_narrative_structure, get_structure_description, get_structure_stages]
