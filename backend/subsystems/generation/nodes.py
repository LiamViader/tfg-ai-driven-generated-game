from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton

def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    return {}

def prepare_refinement(state: GenerationGraphState):
    """Intermidiate node between seed generation and refinement, prepares refinement"""
    print("---ENTERING: PREPARE REFINEMENT NODE---")

    game_state = SimulatedGameStateSingleton.get_instance()
    refined_prompt = game_state.get_refined_prompt()
    assert refined_prompt is not None, "Refined prompt should not be None at prepare refinement"  

    main_goal = game_state.get_main_goal()
    assert main_goal is not None, "Player main goal should not be None at prepare refinement"

    foundational_info = refined_prompt + "\n In this narrative world, the player has the following goal/objective: " + main_goal

    return{
        "refinement_foundational_world_info": foundational_info
    }

def finalize_generation(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    return {}
