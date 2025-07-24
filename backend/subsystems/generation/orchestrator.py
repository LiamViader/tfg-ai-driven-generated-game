from langgraph.graph import StateGraph, END, START

from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.nodes import *
from subsystems.generation.seed.orchestrator import get_seed_generator_graph_app
from subsystems.generation.refinement_loop.orchestrator import get_refinement_loop_graph_app
from typing import Literal

def check_success(state: GenerationGraphState) -> Literal["continue", "end_with_error"]:
    """
    Checks the 'finalized_with_success' flag in the state to determine the next step.
    """
    if state.finalized_with_success:
        print("  - Check: Success. Continuing to next step.")
        return "continue"
    else:
        print("  - Check: Failure detected. Ending generation process.")
        return "end_with_error"

#TODO FER COMPROBACIONS DESPRES DE CADA SUBSYSTEMA PER SI S'HA D'ACABAR EN ERROR O NO. (O FER RETRY)
def get_generation_graph_app():
    """Builds the overall generation graph."""
    workflow = StateGraph(GenerationGraphState)
    seed_sub_graph = get_seed_generator_graph_app()
    refinement_sub_graph = get_refinement_loop_graph_app()

    workflow.add_node("start_generation", start_generation)
    workflow.add_node("seed_generation", seed_sub_graph)
    workflow.add_node("prepare_refinement", prepare_refinement)
    workflow.add_node("refinement_loop", refinement_sub_graph)
    workflow.add_node("post_process", post_process)
    workflow.add_node("generate_images", generate_images)
    workflow.add_node("finalize_generation_success", finalize_generation_success)
    workflow.add_node("finalize_generation_error", finalize_generation_error)

    workflow.add_edge(START, "start_generation")
    workflow.add_edge("start_generation", "seed_generation")
    workflow.add_conditional_edges(
        "seed_generation",
        check_success,
        {
            "continue": "prepare_refinement",
            "end_with_error": "finalize_generation_error"
        }
    )

    workflow.add_edge("prepare_refinement", "refinement_loop")

    workflow.add_conditional_edges(
        "refinement_loop",
        check_success,
        {
            "continue": "post_process",
            "end_with_error": "finalize_generation_error"
        }
    )

    workflow.add_conditional_edges(
        "post_process",
        check_success,
        {
            "continue": "generate_images",
            "end_with_error": "finalize_generation_error"
        }
    )
    
    workflow.add_edge("generate_images", "finalize_generation_success")
    workflow.add_edge("finalize_generation_success", END)
    workflow.add_edge("finalize_generation_error", END)

    app = workflow.compile()
    return app
