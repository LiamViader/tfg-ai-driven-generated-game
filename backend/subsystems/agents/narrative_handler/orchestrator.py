from langgraph.graph import StateGraph, END, START
from subsystems.agents.narrative_handler.schemas.graph_state import NarrativeGraphState
from subsystems.agents.narrative_handler.nodes import *
from langchain_core.messages import ToolMessage


def iteration_limit_exceeded_or_agent_finalized(state: NarrativeGraphState) -> str:
    current_iteration = state.narrative_current_executor_iteration
    max_iterations = state.narrative_max_executor_iterations
    if state.narrative_task_finalized_by_agent or current_iteration >= max_iterations:
        if state.narrative_max_validation_iterations > 0:
            return "finalize_executor_and_validate"
        else:
            return "finalize_executor_and_succeed"
    else:
        return "continue_executor"


def iteration_limit_exceeded_or_agent_validated(state: NarrativeGraphState) -> str:
    current_iteration = state.narrative_current_validation_iteration
    tries_to_evaluate_after_max_iterations = 3
    max_iterations = state.narrative_max_validation_iterations + tries_to_evaluate_after_max_iterations
    if state.narrative_agent_validated or current_iteration >= max_iterations:
        if state.narrative_agent_validation_conclusion_flag:
            return "finalize_success"
        else:
            if state.narrative_current_try <= state.narrative_max_retries:
                return "retry_executor"
            else:
                return "finalize_failure"
    else:
        return "continue_validation"


def get_narrative_graph_app():
    workflow = StateGraph(NarrativeGraphState)

    workflow.add_node("executor_receive_objective", receive_objective_node)
    workflow.add_node("executor_reason", narrative_executor_reason_node)
    workflow.add_node("executor_tool", narrative_executor_tool_node)
    workflow.add_node("validation_receive_result", receive_result_for_validation_node)
    workflow.add_node("validation_reason", narrative_validation_reason_node)
    workflow.add_node("validation_tool", narrative_validation_tool_node)
    workflow.add_node("retry_executor", retry_executor_node)
    workflow.add_node("final_node_success", final_node_success)
    workflow.add_node("final_node_failure", final_node_failure)

    workflow.add_edge(START, "executor_receive_objective")
    workflow.add_edge("executor_receive_objective", "executor_reason")
    workflow.add_edge("executor_reason", "executor_tool")
    workflow.add_conditional_edges(
        "executor_tool",
        iteration_limit_exceeded_or_agent_finalized,
        {
            "continue_executor": "executor_reason",
            "finalize_executor_and_validate": "validation_receive_result",
            "finalize_executor_and_succeed": "final_node_success",
        },
    )
    workflow.add_edge("validation_receive_result", "validation_reason")
    workflow.add_edge("validation_reason", "validation_tool")
    workflow.add_conditional_edges(
        "validation_tool",
        iteration_limit_exceeded_or_agent_validated,
        {
            "continue_validation": "validation_reason",
            "finalize_success": "final_node_success",
            "finalize_failure": "final_node_failure",
            "retry_executor": "retry_executor",
        },
    )
    workflow.add_edge("retry_executor", "executor_reason")
    workflow.add_edge("final_node_success", END)
    workflow.add_edge("final_node_failure", END)

    app = workflow.compile()
    return app
