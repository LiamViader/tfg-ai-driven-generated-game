from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton

def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    return {}

def update_game_state_seed(state: GenerationGraphState):
    """Updates the game state adding all the generated info"""
    print("---ENTERING: UPDATE GAME STATE SEED---")
    game_state = SimulatedGameStateSingleton.get_instance()
    
    return {}

def finalize_generation(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    return {}
