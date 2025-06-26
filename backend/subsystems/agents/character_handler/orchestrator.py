"""Graph orchestrator for the character agent."""

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import ToolMessage

from .schemas.graph_state import CharacterGraphState
from .nodes import (
    receive_objective_node,
    character_executor_reason_node,
    character_executor_tool_node,
    receive_result_for_validation_node,
    character_validation_reason_node,
    character_validation_tool_node,
    retry_executor_node,
    final_node_success,
    final_node_failure,
)


def iteration_limit_exceeded_or_agent_finalized(state: CharacterGraphState) -> str:
    current_iteration = state.characters_current_executor_iteration
    max_iterations = state.characters_max_executor_iterations
    if state.characters_task_finalized_by_agent or current_iteration >= max_iterations:
        if state.characters_max_validation_iterations > 0:
            return "finalize_executor_and_validate"
        else:
            return "finalize_executor_and_succeed"
    else:
        return "continue_executor"


def iteration_limit_exceeded_or_agent_validated(state: CharacterGraphState) -> str:
    current_iteration = state.characters_current_validation_iteration
    tries_to_evaluate_after_max_iterations = 3
    max_iterations = state.characters_max_validation_iterations + tries_to_evaluate_after_max_iterations
    if state.characters_agent_validated or current_iteration >= max_iterations:
        if state.characters_agent_validation_conclusion_flag:
            return "finalize_success"
        else:
            if state.characters_current_try <= state.characters_max_retries:
                return "retry_executor"
            else:
                return "finalize_failure"
    else:
        return "continue_validation"


def get_character_graph_app():
    workflow = StateGraph(CharacterGraphState)

    workflow.add_node("executor_receive_objective", receive_objective_node)
    workflow.add_node("executor_reason", character_executor_reason_node)
    workflow.add_node("executor_tool", character_executor_tool_node)
    workflow.add_node("validation_receive_result", receive_result_for_validation_node)
    workflow.add_node("validation_reason", character_validation_reason_node)
    workflow.add_node("validation_tool", character_validation_tool_node)
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

