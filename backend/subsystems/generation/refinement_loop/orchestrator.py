from typing import Union, Literal
from langgraph.graph import StateGraph, END, START
from enum import Enum
from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.refinement_loop.nodes import *
from subsystems.summarize_agent_logs.orchestrator import get_summarize_graph_app
from subsystems.generation.refinement_loop.constants import AgentName
from subsystems.agents.map_handler.orchestrator import get_map_graph_app
from subsystems.agents.character_handler.orchestrator import get_character_graph_app
from subsystems.agents.relationship_handler.orchestrator import get_relationship_graph_app
from subsystems.agents.narrative_handler.orchestrator import get_narrative_graph_app
from subsystems.agents.game_event_handler.orchestrator import get_game_event_graph_app

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
    characters_agent_sub_graph = get_character_graph_app()
    relationship_agent_sub_graph = get_relationship_graph_app()
    narrative_agent_sub_graph = get_narrative_graph_app()
    events_agent_sub_graph = get_game_event_graph_app()

    workflow.add_node("start_refinement_loop", start_refinement_loop)
    workflow.add_node("map_agent", map_agent_sub_graph)
    workflow.add_node("map_step_start", map_step_start)
    workflow.add_node("map_step_finish", map_step_finish)
    workflow.add_node("characters_agent", characters_agent_sub_graph)
    workflow.add_node("characters_step_start", characters_step_start)
    workflow.add_node("characters_step_finish", characters_step_finish)
    workflow.add_node("relationship_agent", relationship_agent_sub_graph)
    workflow.add_node("relationship_step_start", relationship_step_start)
    workflow.add_node("relationship_step_finish", relationship_step_finish)
    workflow.add_node("narrative_agent", narrative_agent_sub_graph)
    workflow.add_node("narrative_step_start", narrative_step_start)
    workflow.add_node("narrative_step_finish", narrative_step_finish)
    workflow.add_node("events_agent", events_agent_sub_graph)
    workflow.add_node("events_step_start", events_step_start)
    workflow.add_node("events_step_finish", events_step_finish)
    workflow.add_node("finalize_step", finalize_step)
    workflow.add_node("prepare_next_step", prepare_next_step)
    workflow.add_node("summarize_agent_logs", summarize_sub_graph)
    workflow.add_node("add_summarized_agent_log", add_agent_log_to_changelog)
    workflow.add_node("finalize_refinement_loop", finalize_refinement_loop)



    workflow.add_edge(START, "start_refinement_loop")
    workflow.add_conditional_edges(
        "start_refinement_loop",
        go_to_next_agent_or_finish,
        {
            AgentName.MAP: "map_step_start",
            AgentName.CHARACTERS: "characters_step_start",
            AgentName.RELATIONSHIP: "relationship_step_start",
            AgentName.NARRATIVE: "narrative_step_start",
            AgentName.EVENTS: "events_step_start",
            "finalize": "finalize_refinement_loop",
        }
    )

    workflow.add_conditional_edges(
        "prepare_next_step",
        go_to_next_agent_or_finish,
        {
            AgentName.MAP: "map_step_start",
            AgentName.CHARACTERS: "characters_step_start",
            AgentName.RELATIONSHIP: "relationship_step_start",
            AgentName.NARRATIVE: "narrative_step_start",
            AgentName.EVENTS: "events_step_start",
            "finalize": "finalize_refinement_loop",
        }
    )


    workflow.add_edge("map_step_start", "map_agent")
    workflow.add_edge("map_agent", "map_step_finish")
    workflow.add_edge("map_step_finish", "finalize_step")

    workflow.add_edge("characters_step_start", "characters_agent")
    workflow.add_edge("characters_agent", "characters_step_finish")
    workflow.add_edge("characters_step_finish", "finalize_step")

    workflow.add_edge("relationship_step_start", "relationship_agent")
    workflow.add_edge("relationship_agent", "relationship_step_finish")
    workflow.add_edge("relationship_step_finish", "finalize_step")

    workflow.add_edge("narrative_step_start", "narrative_agent")
    workflow.add_edge("narrative_agent", "narrative_step_finish")
    workflow.add_edge("narrative_step_finish", "finalize_step")

    workflow.add_edge("events_step_start", "events_agent")
    workflow.add_edge("events_agent", "events_step_finish")
    workflow.add_edge("events_step_finish", "finalize_step")

    workflow.add_conditional_edges(
        "finalize_step",
        last_step_result,
        {
            "success": "summarize_agent_logs",
            "failure": "prepare_next_step",
        }
    )
    workflow.add_edge("summarize_agent_logs", "add_summarized_agent_log")
    workflow.add_edge("add_summarized_agent_log", "prepare_next_step")
    workflow.add_edge("finalize_refinement_loop", END)

    app = workflow.compile()
    return app