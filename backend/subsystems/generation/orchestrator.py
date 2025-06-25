from langgraph.graph import StateGraph, END, START

from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.nodes import start_generation, finalize_generation
from subsystems.generation.seed.orchestrator import get_seed_generator_graph_app
from subsystems.generation.refinement_loop.orchestrator import get_refinement_loop_graph_app


def get_generation_graph_app():
    """Builds the overall generation graph."""
    workflow = StateGraph(GenerationGraphState)
    seed_sub_graph = get_seed_generator_graph_app()
    refinement_sub_graph = get_refinement_loop_graph_app()

    workflow.add_node("start_generation", start_generation)
    workflow.add_node("seed_generation", seed_sub_graph)
    workflow.add_node("refinement_loop", refinement_sub_graph)
    workflow.add_node("finalize_generation", finalize_generation)

    workflow.add_edge(START, "start_generation")
    workflow.add_edge("start_generation", "seed_generation")
    workflow.add_edge("seed_generation", "refinement_loop")
    workflow.add_edge("refinement_loop", "finalize_generation")
    workflow.add_edge("finalize_generation", END)

    app = workflow.compile()
    return app
