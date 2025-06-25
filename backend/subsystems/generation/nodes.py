from subsystems.generation.schemas.graph_state import GenerationGraphState


def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    return {}


def finalize_generation(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    return {}
