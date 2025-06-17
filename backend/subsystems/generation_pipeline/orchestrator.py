from langgraph.graph import StateGraph, END, START
from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.nodes import *
from langchain_core.messages import ToolMessage

def validate_refined_prompt(state: GenerationGraphState) -> str:
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

def validate_main_goal(state: GenerationGraphState) -> str:
    """
    Determines whether to continue to the reasoning node, retry or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    if state.main_goal != "" and state.generate_main_goal_error_message == "":
        return "continue"
    else:
        current_attempt = state.generate_main_goal_attempts
        max_attempts = state.generate_main_goal_max_attempts

        if current_attempt<max_attempts:
            return "retry"
        else:
            return "end_by_error"

def structure_selected_or_reason_again(state: GenerationGraphState) -> str:
    """Check if a narrative structure has been selected."""
    print(state.selected_structure)
    if state.selected_structure is not None:
        return "continue"
    elif state.current_structure_selection_iteration < state.max_structure_selection_reason_iterations + state.max_structure_forced_selection_iterations:
        return "reason"
    else:
        return "end_by_error"



def get_generator_graph_app():
    """
    Builds and compiles the map generation graph.
    """
    workflow = StateGraph(GenerationGraphState)

    workflow.add_node("receive_generation_prompt", receive_generation_prompt)
    workflow.add_node("refine_generation_prompt", refine_generation_prompt)
    workflow.add_node("generate_main_goal", generate_main_goal)
    workflow.add_node("narrative_structure_reason", narrative_structure_reason_node)
    workflow.add_node("narrative_structure_tool", narrative_structure_tool_node)

    workflow.add_edge(START, "receive_generation_prompt")
    workflow.add_edge("receive_generation_prompt", "refine_generation_prompt")
    workflow.add_edge("refine_generation_prompt", "generate_main_goal")
    workflow.add_edge("generate_main_goal", "narrative_structure_reason")
    workflow.add_edge("narrative_structure_reason", "narrative_structure_tool")
    workflow.add_conditional_edges(
        "refine_generation_prompt",
        validate_refined_prompt,
        {
            "continue": "generate_main_goal",
            "retry": "refine_generation_prompt",
            "end_by_error": END
        }
    )
    workflow.add_conditional_edges(
        "generate_main_goal",
        validate_main_goal,
        {
            "continue": "narrative_structure_reason",
            "retry": "generate_main_goal",
            "end_by_error": END
        }
    )
    workflow.add_conditional_edges(
        "narrative_structure_tool",
        structure_selected_or_reason_again,
        {
            "continue": END,
            "reason": "narrative_structure_reason",
            "end_by_error": END,
        }
    )

    app = workflow.compile()
    return app