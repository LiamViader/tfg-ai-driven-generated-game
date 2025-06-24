from langgraph.graph import StateGraph, END, START
from subsystems.summarize.schemas.graph_state import SummarizeGraphState
from subsystems.summarize.nodes import receive_operations_log_node, summarize_operations_node


def get_summarize_graph_app():
    """
    Constructs and compiles the summarize graph application.
    It summarizes a set of world-modifying operations into a narrative description.
    """

    workflow = StateGraph(SummarizeGraphState)

    workflow.add_node("receive_operations_log", receive_operations_log_node)
    workflow.add_node("summarize_operations", summarize_operations_node)

    workflow.add_edge(START, "receive_operations_log")
    workflow.add_edge("receive_operations_log", "summarize_operations")
    workflow.add_edge("summarize_operations", END)


    app = workflow.compile()
    return app