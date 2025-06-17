"""Graph orchestrator for the relationship agent."""

from langgraph.graph import StateGraph, END, START
from langchain_core.messages import ToolMessage

from .schemas.graph_state import RelationshipGraphState
from .nodes import (
    receive_objective_node,
    relationship_executor_reason_node,
    relationship_executor_tool_node,
)


def iteration_limit_exceeded(state: RelationshipGraphState) -> str:
    if state.current_executor_iteration >= state.max_executor_iterations or state.working_simulated_relationships.task_finalized_by_agent:
        return "finalize"
    return "continue"


def get_relationship_graph_app():
    workflow = StateGraph(RelationshipGraphState)

    workflow.add_node("receive_objective", receive_objective_node)
    workflow.add_node("executor_reason", relationship_executor_reason_node)
    workflow.add_node("executor_tool", relationship_executor_tool_node)

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
