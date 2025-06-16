"""Graph orchestrator for the character agent."""

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import ToolMessage

from .schemas.graph_state import CharacterGraphState
from .nodes import (
    receive_objective_node,
    character_executor_reason_node,
    character_executor_tool_node,
)


def iteration_limit_exceeded(state: CharacterGraphState) -> str:
    if state.current_executor_iteration >= state.max_executor_iterations or state.working_simulated_characters.task_finalized_by_agent:
        return "finalize"
    return "continue"


def get_character_graph_app():
    workflow = StateGraph(CharacterGraphState)

    workflow.add_node("receive_objective", receive_objective_node)
    workflow.add_node("executor_reason", character_executor_reason_node)
    workflow.add_node("executor_tool", character_executor_tool_node)

    workflow.add_edge(START, "receive_objective")
    workflow.add_edge("receive_objective", "executor_reason")
    workflow.add_edge("executor_reason", "executor_tool")
    workflow.add_conditional_edges(
        "executor_tool",
        iteration_limit_exceeded,
        {
            "continue": "executor_reason",
            "finalize": END,
        },
    )

    app = workflow.compile()
    return app

