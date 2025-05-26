from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..schemas.graph_state import MapGraphState
from ..schemas.map_elements import ScenarioModel


BASE_RULES_AND_CONSTRAINTS = [
    "Every scenario must be connected to at least one other scenario.",
    "All scenarios must belong to a single connected graph. There should be no disconnected clusters of scenarios."
]


class GraphInitialInput(BaseModel):
    current_objective: str = Field(..., description="The high-level textual goal for the map task.")
    global_narrative_context: str = Field(..., description="Overall world lore and narrative context.")
    extra_map_rules_and_constraints: Optional[List[str]] = Field(default_factory=list, description="Extra rules and constraints for the map system.")
    initial_scenarios: Optional[Dict[str, ScenarioModel]] = Field(default_factory=dict, description="Optional scenarios to start with.")
    max_refinement_attempts: Optional[int] = Field(3, description="Optional override for maximum refinement attempts for the objective.")

def receive_objective_node(initial_input: GraphInitialInput) -> MapGraphState:
    """
    First node of the graph.
    Takes the initial input and constructs de the MapGraphState object.
    """
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")

    state = MapGraphState(
        global_narrative_context=initial_input.global_narrative_context,
        map_rules_and_constraints=initial_input.extra_map_rules_and_constraints + BASE_RULES_AND_CONSTRAINTS,
        current_objective=initial_input.current_objective,
        scenarios=initial_input.initial_scenarios,
        history_log=["Objective received: " + initial_input.current_objective],
        initial_map_generation_complete=False,
        current_refinement_attempts=0,
        max_refinement_attempts=initial_input.max_refinement_attempts,
        plan_outcome_is_valid=False,
        # ...otros campos de MapGraphState con sus valores iniciales
    )
        
    print(f"Initial state created for objective: {state.current_objective}")

    return state

