from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton

def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    return {}

def check_generated_seed(state: GenerationGraphState):
    """Updates the game state adding all the generated info"""
    print("---ENTERING: UPDATE GAME STATE SEED---")

    return {}

def finalize_generation(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    return {}
