from langgraph.graph import StateGraph, END, START
from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.nodes import receive_objective_node, map_reason_node, map_executor_node, map_executor_node
from langchain_core.messages import ToolMessage

def iteration_limit_exceeded_or_agent_finalized(state: MapGraphState) -> str:
    """
    Determines whether to continue to the reasoning node or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    current_iteration = state.current_iteration
    max_iterations = state.max_iterations
    if state.working_simulated_map.task_finalized_by_agent or current_iteration >= max_iterations:
        return "finalize"
    else:
        return "continue"


def get_map_graph_app():
    """
    Builds and compiles the map generation graph.
    """
    workflow = StateGraph(MapGraphState)

    workflow.add_node("receive_objective", receive_objective_node)
    workflow.add_node("reason", map_reason_node)
    workflow.add_node("execute", map_executor_node)

    workflow.add_edge(START, "receive_objective")
    workflow.add_edge("receive_objective", "reason")
    workflow.add_edge("reason", "execute")
    workflow.add_conditional_edges(
        "execute",
        iteration_limit_exceeded_or_agent_finalized,
        {
            "continue": "reason",
            "finalize": END
        }
    )

    # Compile the graph into a runnable app
    app = workflow.compile()
    return app