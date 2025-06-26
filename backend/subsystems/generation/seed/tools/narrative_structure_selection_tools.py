from typing import Annotated, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from core_game.narrative.structures import AVAILABLE_NARRATIVE_STRUCTURES
from subsystems.generation.schemas.graph_state import GenerationGraphState

# Helper mapping from id to structure
AVAILABLE_STRUCTURES_BY_ID = {s.id: s for s in AVAILABLE_NARRATIVE_STRUCTURES}

class ToolSelectStructureArgs(BaseModel):
    justification: str = Field(..., description="Short explanation of why this structure is chosen")
    structure_id: str = Field(..., description="ID of the narrative structure to select")
    tool_call_id: Annotated[str, InjectedToolCallId]

class ToolGetStructureInfoArgs(BaseModel):
    structure_id: str = Field(..., description="ID of the structure")

@tool(args_schema=ToolSelectStructureArgs)
def select_narrative_structure(justification: str, structure_id: str, tool_call_id: Annotated[str, InjectedToolCallId]) -> Command:
    """Select one of the available narrative structures by its id."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return Command(update={
            "structure_selection_messages": [
                ToolMessage(
                    f"Structure id '{structure_id}' not found",
                    tool_call_id=tool_call_id
                )
            ]
        })
    
    else:
        return Command(update={
            "selected_structure": struct,
            "structure_selection_justification": justification,
            # update the message history
            "structure_selection_messages": [
                ToolMessage(
                    f"Selected narrative structure '{struct.name}'",
                    tool_call_id=tool_call_id
                )
            ]
        })

@tool(args_schema=ToolGetStructureInfoArgs)
def get_structure_description(structure_id: str) -> str:
    """Get description and use cases of a narrative structure."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return f"Structure id '{structure_id}' not found"
    return f"{struct.name} ({structure_id}): {struct.description} Use cases: {struct.orientative_use_cases}"

@tool(args_schema=ToolGetStructureInfoArgs)
def get_structure_stages(structure_id: str) -> str:
    """List the stages of the given structure."""
    struct = AVAILABLE_STRUCTURES_BY_ID.get(structure_id)
    if struct is None:
        return f"Structure id '{structure_id}' not found"
    return "\n".join([f"{i+1}. {stage.name}: {stage.narrative_objectives}" for i, stage in enumerate(struct.stages)])

STRUCTURE_TOOLS = [select_narrative_structure, get_structure_description, get_structure_stages]
