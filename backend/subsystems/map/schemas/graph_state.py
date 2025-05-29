from typing import Dict, List, Optional, Any, Annotated, Sequence
from pydantic import BaseModel, Field
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# El '.' significa "desde el directori actual (schemas)"
from subsystems.map.schemas.map_elements import ScenarioModel, Direction, OppositeDirections
from subsystems.map.schemas.simulated_map import SimulatedMapModel
from subsystems.map.schemas.simulated_map import ListScenariosClusterSummaryArgs



class MapGraphState(BaseModel):
    # Context and objectives
    global_narrative_context: str = Field(..., description="Narrative background and context of the world—its lore, themes, key story elements, etc—that must be considered while solving the objective.")
    map_rules_and_constraints: List[str] = Field(..., description="Explicit world-building rules or design constraints that must be respected when constructing or validating the map. These can include logical requirements (e.g., 'an exterior scenario connected to an interior one must feature a visible transition like a door or gate') or aesthetic guidelines that ensure internal consistency and visual coherence across the world.")
    current_objective: str = Field(..., description="The high-level textual goal for the current map generation/modification task.")
    requesting_agent_id: Optional[str] = Field(None, description="ID of the game agent requesting a change (if applicable).")
    initial_map_summary: str = Field(default="", description="Initial summary of the map when starting the workflow")

    # Map Data
    scenarios: Dict[str, ScenarioModel] = Field(default_factory=dict, description="All scenarios in the map, keyed by their unique ID.")

    # --- Working memo ---
    working_simulated_map: SimulatedMapModel = Field(default_factory=SimulatedMapModel, description="Represents the current working state of the simulated map being built or modified during the session. Serves as the agent's active memory of the map.")
    messages: Annotated[Sequence[BaseMessage], add_messages] = Field(default_factory=list, description="Messages holding intermediate steps.")
    current_iteration: int = Field(default=0, description="Current iteration the react cycle is on")
    max_iterations: int = Field(..., description="Max iterations of the react cycle before finishing")

    # --- Logs and flux control ---
    history_log: List[str] = Field(default_factory=list, description="A log of objectives, plans, validations, and outcomes for debugging and tracing.")
    previous_feedback: str = Field(..., description="Feedback from last retry")

    @staticmethod
    def get_opposite_direction(direction: Direction) -> Direction: # Usas Direction importada
        """Helper method to get the opposite of a given direction."""
        return OppositeDirections[direction] # Usas OppositeDirections importado

    def reset_working_memory(self):
        initial_working_simulated_map = SimulatedMapModel(
            simulated_scenarios=deepcopy(self.scenarios),
        )
        self.working_simulated_map = initial_working_simulated_map
        self.messages = []
        self.current_iteration = 0
        self.initial_map_summary = self.working_simulated_map.get_summary_list()