from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence
from langchain_core.messages import BaseMessage

from .schemas.graph_state import RelationshipGraphState
from .prompts.reasoning import format_relationship_reason_prompt
from .tools.relationship_tools import EXECUTORTOOLS
from utils.message_window import get_valid_messages_window


def receive_objective_node(state: RelationshipGraphState) -> RelationshipGraphState:
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    state.reset_working_memory()
    return state


def relationship_executor_reason_node(state: RelationshipGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")
    llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")
    full_prompt = format_relationship_reason_prompt(
        narrative_context=state.global_narrative_context,
        relationship_rules_and_constraints=state.relationship_rules_and_constraints,
        initial_relationships_summary="",
        objective=state.current_objective,
        other_guidelines=state.other_guidelines,
        messages=get_valid_messages_window(state.executor_messages, 30),
    )
    state.current_executor_iteration += 1
    response = llm.invoke(full_prompt)
    return {
        "executor_messages": [response],
        "current_executor_iteration": state.current_executor_iteration,
    }


relationship_executor_tool_node = ToolNode(EXECUTORTOOLS)
relationship_executor_tool_node.messages_key = "executor_messages"
