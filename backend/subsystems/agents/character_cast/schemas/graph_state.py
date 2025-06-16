
from typing import Dict, List, Optional, Sequence, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from core_game.character.schemas import CharacterBaseModel
from .simulated_characters import SimulatedCharactersModel


class CharacterGraphState(BaseModel):
    """Holds context and working memory for the character agent."""

    global_narrative_context: str = Field(..., description="Narrative context provided to the agent to operate.")
    character_rules_and_constraints: List[str] = Field(..., description="Rules or constraints for the character agent to follow.")
    current_objective: str = Field(..., description="Current objective")
    other_guidelines: str = Field(..., description="Additional softer guidelines")

    characters: Dict[str, CharacterBaseModel] = Field(default_factory=dict)

    working_simulated_characters: SimulatedCharactersModel = Field(default_factory=SimulatedCharactersModel)

    executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages holding intermediate steps. For the Executor agent")
    current_executor_iteration: int = Field(default=0, description="Current iteration the react cycle is on")
    max_executor_iterations: int = Field(..., description="Maximum iterations for the executor to achieve the objective.")

    def reset_working_memory(self) -> None:
        self.working_simulated_characters = SimulatedCharactersModel(simulated_characters=self.characters.copy())
        self.executor_messages = []
        self.current_executor_iteration = 0
