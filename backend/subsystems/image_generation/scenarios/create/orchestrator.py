from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from .schemas import GraphState
from .nodes import process_all_scenarios_node

def get_main_orchestrator_app() -> Runnable:
    builder = StateGraph(GraphState)

    builder.add_node("process_all_scenarios", process_all_scenarios_node)

    builder.set_entry_point("process_all_scenarios")

    builder.add_edge("process_all_scenarios", END)

    main_orchestrator = builder.compile()
    
    return main_orchestrator