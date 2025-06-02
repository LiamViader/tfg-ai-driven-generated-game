from langgraph.graph import StateGraph, END, START
from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.nodes import receive_objective_node, map_executor_reason_node, map_executor_tool_node, map_validation_reason_node, receive_result_for_validation_node, map_validation_tool_node
from langchain_core.messages import ToolMessage

def iteration_limit_exceeded_or_agent_finalized(state: MapGraphState) -> str:
    """
    Determines whether to continue to the reasoning node or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    current_iteration = state.current_executor_iteration
    max_iterations = state.max_executor_iterations
    if state.working_simulated_map.task_finalized_by_agent or current_iteration >= max_iterations:
        return "finalize"
    else:
        return "continue"

def iteration_limit_exceeded_or_agent_validated(state: MapGraphState) -> str:
    """
    Determines whether to continue to the reasoning node or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    current_iteration = state.current_validation_iteration
    max_iterations = state.max_validation_iterations
    if state.working_simulated_map.agent_validated or current_iteration >= max_iterations:
        return "finalize"
    else:
        return "continue"

def get_map_graph_app():
    """
    Builds and compiles the map generation graph.
    """
    workflow = StateGraph(MapGraphState)

    workflow.add_node("executor_receive_objective", receive_objective_node)
    workflow.add_node("executor_reason", map_executor_reason_node)
    workflow.add_node("executor_tool", map_executor_tool_node)
    workflow.add_node("validation_receive_result", receive_result_for_validation_node)
    workflow.add_node("validation_reason", map_validation_reason_node)
    workflow.add_node("validation_tool", map_validation_tool_node)

    workflow.add_edge(START, "executor_receive_objective")
    workflow.add_edge("executor_receive_objective", "executor_reason")
    workflow.add_edge("executor_reason", "executor_tool")
    workflow.add_conditional_edges(
        "executor_tool",
        iteration_limit_exceeded_or_agent_finalized,
        {
            "continue": "executor_reason",
            "finalize": "validation_receive_result"
        }
    )
    workflow.add_edge("validation_receive_result", "validation_reason")
    workflow.add_edge("validation_reason", "validation_tool")
    workflow.add_conditional_edges(
        "validation_tool",
        iteration_limit_exceeded_or_agent_validated,
        {
            "continue": "validation_reason",
            "finalize": END
        }
    )

    # Compile the graph into a runnable app
    app = workflow.compile()
    return app