"""Nodes for the character agent graph."""

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence
from langchain_core.messages import BaseMessage

from .schemas.graph_state import CharacterGraphState
from .prompts.character_reasoning import format_character_reason_prompt
from .tools.character_tools import EXECUTORTOOLS
from utils.message_window import get_valid_messages_window


def receive_objective_node(state: CharacterGraphState) -> CharacterGraphState:
    state.reset_working_memory()
    return state


def character_executor_reason_node(state: CharacterGraphState):
    llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")
    full_prompt = format_character_reason_prompt(
        initial_characters_summary=state.working_simulated_characters.get_summary(),
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


character_executor_tool_node = ToolNode(EXECUTORTOOLS)
character_executor_tool_node.messages_key = "executor_messages"

