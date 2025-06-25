from typing import Union, Literal
from langgraph.graph import StateGraph, END, START
from enum import Enum
from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.refinement_loop.nodes import *
from subsystems.summarize_agent_logs.orchestrator import get_summarize_graph_app
from subsystems.generation.refinement_loop.constants import AgentName
from subsystems.agents.map_handler.orchestrator import get_map_graph_app


def go_to_next_agent_or_finish(state: RefinementLoopGraphState) -> Union[AgentName, Literal["finalize"]]:
    """
    Determines where to go based on the current step agent.
    """
    if state.refinement_current_pass<len(state.refinement_pipeline_config.steps):
        current_step = state.refinement_pipeline_config.steps[state.refinement_current_pass]
        return current_step.agent_name
    else:
        return "finalize"

def last_step_result(state: RefinementLoopGraphState) -> str:
    """
    Determines whether the las step succeeded or not.
    """
    if state.last_step_succeeded:
        return "success"
    else:
        return "failure"


def get_refinement_loop_graph_app():
    """
    Builds and compiles the map generation graph.
    """
    workflow = StateGraph(RefinementLoopGraphState)
    summarize_sub_graph = get_summarize_graph_app()
    map_agent_sub_graph = get_map_graph_app()

    workflow.add_node("start_refinement_loop", start_refinement_loop)
    workflow.add_node("map_agent", map_agent_sub_graph)
    workflow.add_node("map_step_start", map_step_start)
    workflow.add_node("map_step_finish", map_step_finish)
    workflow.add_node("finalize_step", finalize_step)
    workflow.add_node("prepare_next_step", prepare_next_step)
    workflow.add_node("summarize_agent_logs", summarize_sub_graph)



    workflow.add_edge(START, "start_refinement_loop")
    workflow.add_conditional_edges(
        "start_refinement_loop",
        go_to_next_agent_or_finish,
        {
            AgentName.MAP: "map_step_start",
            "finalize": END,
        }
    )

    workflow.add_conditional_edges(
        "prepare_next_step",
        go_to_next_agent_or_finish,
        {
            AgentName.MAP: "map_step_start",
            "finalize": END,
        }
    )


    workflow.add_edge("map_step_start", "map_agent")
    workflow.add_edge("map_agent", "map_step_finish")
    workflow.add_edge("map_step_finish", "finalize_step")


    workflow.add_conditional_edges(
        "finalize_step",
        last_step_result,
        {
            "success": "summarize_agent_logs",
            "failure": "prepare_next_step",
        }
    )
    workflow.add_edge("summarize_agent_logs", "prepare_next_step")


    app = workflow.compile()
    return app