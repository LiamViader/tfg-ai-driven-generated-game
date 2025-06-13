from langgraph.graph import StateGraph, END, START
from subsystems.agents.map.schemas.graph_state import MapGraphState
from subsystems.agents.map.nodes import *
from langchain_core.messages import ToolMessage

def iteration_limit_exceeded_or_agent_finalized(state: MapGraphState) -> str:
    """
    Determines whether to continue to the reasoning node or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    current_iteration = state.current_executor_iteration
    max_iterations = state.max_executor_iterations
    if state.working_simulated_map.task_finalized_by_agent or current_iteration >= max_iterations:
        return "finalize_executor"
    else:
        return "continue_executor"

def iteration_limit_exceeded_or_agent_validated(state: MapGraphState) -> str:
    """
    Determines whether to continue to the reasoning node or end the process
    based on the iteration count and task completion (agent called finalize_task).
    """
    current_iteration = state.current_validation_iteration
    tries_to_evaluate_after_max_iterations = 4
    max_iterations = state.max_validation_iterations + tries_to_evaluate_after_max_iterations
    if state.working_simulated_map.agent_validated or current_iteration >= max_iterations:
        if state.current_try <= state.max_retries and not state.working_simulated_map.agent_validation_conclusion_flag:
            return "retry_executor"
        else:
            return "finalize"
    else:
        return "continue_validation"

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
    workflow.add_node("retry_executor", retry_executor_node)

    workflow.add_edge(START, "executor_receive_objective")
    workflow.add_edge("executor_receive_objective", "executor_reason")
    workflow.add_edge("executor_reason", "executor_tool")
    workflow.add_conditional_edges(
        "executor_tool",
        iteration_limit_exceeded_or_agent_finalized,
        {
            "continue_executor": "executor_reason",
            "finalize_executor": "validation_receive_result"
        }
    )
    workflow.add_edge("validation_receive_result", "validation_reason")
    workflow.add_edge("validation_reason", "validation_tool")
    workflow.add_conditional_edges(
        "validation_tool",
        iteration_limit_exceeded_or_agent_validated,
        {
            "continue_validation": "validation_reason",
            "finalize": END,
            "retry_executor": "retry_executor"
        }
    )
    workflow.add_edge("retry_executor", "executor_reason")

    # Compile the graph into a runnable app
    app = workflow.compile()
    return app