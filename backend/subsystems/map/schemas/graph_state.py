from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

# El '.' significa "desde el directori actual (schemas)"
from .map_elements import ScenarioModel, Direction, OppositeDirections

class MapGraphState(BaseModel):
    # Context and objectives
    global_narrative_context: str = Field(..., description="Narrative background and context of the world—its lore, themes, key story elements, etc—that must be considered while solving the objective.")
    map_rules_and_constraints: List[str] = Field(..., description="Explicit world-building rules or design constraints that must be respected when constructing or validating the map. These can include logical requirements (e.g., 'an exterior scenario connected to an interior one must feature a visible transition like a door or gate') or aesthetic guidelines that ensure internal consistency and visual coherence across the world.")
    current_objective: str = Field(..., description="The high-level textual goal for the current map generation/modification task.")
    requesting_agent_id: Optional[str] = Field(None, description="ID of the game agent requesting a change (if applicable).")

    # Map Data
    scenarios: Dict[str, ScenarioModel] = Field(default_factory=dict, description="All scenarios in the map, keyed by their unique ID.")

    # --- Memoria de Trabajo del Agente Razonador ---
    proposed_plan: Optional[List[Dict]] = Field(None, description="The sequence of map operations proposed by the reasoning agent.") # Each dict is a MapOperation
    plan_justification: Optional[str] = Field(None, description="The reasoning agent's justification for the proposed plan.")
    validation_feedback: Optional[str] = Field(None, description="Feedback from the validation agent regarding the last proposed plan.")

    # --- Control de Flujo y Logs ---
    history_log: List[str] = Field(default_factory=list, description="A log of objectives, plans, validations, and outcomes for debugging and tracing.")
    initial_map_generation_complete: bool = Field(False, description="Flag indicating if the initial phase of map generation is complete.")
    max_refinement_attempts: int = Field(3, description="Maximum number of attempts the reasoning agent gets to refine a failed plan for the current objective.")
    current_refinement_attempts: int = Field(0, description="Current count of refinement attempts for the active plan.")
    plan_outcome_is_valid: bool = Field(False, description="Flag set by the validation node indicating if the latest plan's outcome was deemed valid.")

    @staticmethod
    def get_opposite_direction(direction: Direction) -> Direction: # Usas Direction importada
        """Helper method to get the opposite of a given direction."""
        return OppositeDirections[direction] # Usas OppositeDirections importado
