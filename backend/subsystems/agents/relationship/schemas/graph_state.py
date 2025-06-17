from typing import Dict, List, Sequence, Optional, Annotated
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from core_game.character.schemas import RelationshipType, CharacterRelationship
from .simulated_relationships import SimulatedRelationshipsModel


class RelationshipGraphState(BaseModel):
    global_narrative_context: str = Field(..., description="Narrative context for the agent")
    relationship_rules_and_constraints: List[str] = Field(..., description="Rules or constraints for managing relationships")
    current_objective: str = Field(..., description="Current objective")
    other_guidelines: str = Field(..., description="Additional guidelines")

    relationship_types: Dict[str, RelationshipType] = Field(default_factory=dict)
    relationships_matrix: Dict[str, Dict[str, Dict[str, CharacterRelationship]]] = Field(default_factory=dict)

    working_simulated_relationships: SimulatedRelationshipsModel = Field(default_factory=SimulatedRelationshipsModel)

    executor_messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list)
    current_executor_iteration: int = Field(default=0)
    max_executor_iterations: int = Field(...)

    def reset_working_memory(self) -> None:
        self.working_simulated_relationships = SimulatedRelationshipsModel(
            relationship_types=self.relationship_types.copy(),
            relationships_matrix={cid: {tid: rels.copy() for tid, rels in targets.items()} for cid, targets in self.relationships_matrix.items()},
        )
        self.executor_messages = []
        self.current_executor_iteration = 0
