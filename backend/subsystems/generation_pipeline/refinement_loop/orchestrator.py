from langgraph.graph import StateGraph, END, START
from subsystems.generation_pipeline.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation_pipeline.refinement_loop.nodes import *
from subsystems.summarize_agent_logs.orchestrator import get_summarize_graph_app

def validate_refined_prompt(state: RefinementLoopGraphState) -> str:
    """
    Determines whether to continue to the next node or end/retry based on the refined prompt validation.
    """
    if state.refine_generation_prompt_error_message == "":
        return "continue"
    else:
        current_attempt = state.refine_generation_prompt_attempts
        max_attempts = state.refine_generation_prompt_max_attempts
        if current_attempt < max_attempts:
            return "retry"
        else:
            return "end_by_error"



def get_refinement_loop_graph_app():
    """
    Builds and compiles the map generation graph.
    """
    workflow = StateGraph(RefinementLoopGraphState)
    summarize_sub_graph = get_summarize_graph_app()

    workflow.add_node("start_refinement_loop", start_refinement_loop)
    workflow.add_node("map_step_start", map_step_start)
    workflow.add_node("map_step_finish", map_step_finish)
    workflow.add_node("prepare_next_step", prepare_next_step)
    workflow.add_node("summarize_agent_logs", summarize_sub_graph)



    workflow.add_edge(START, "start_refinement_loop")
    


    app = workflow.compile()
    return app