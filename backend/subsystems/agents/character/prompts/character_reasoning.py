"""Prompt formatting utilities for the character agent."""

from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage


SYSTEM_PROMPT = """You are 'CharacterAI', an expert character designer for narrative driven games.\nUse the provided tools to create or modify characters until the given objective is satisfied."""

HUMAN_PROMPT = """Objective: {objective}\nOther guidelines: {other_guidelines}\nCurrent characters summary: {initial_characters_summary}"""

SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt = ChatPromptTemplate([SYSTEM_TEMPLATE, HUMAN_TEMPLATE, MessagesPlaceholder(variable_name="agent_scratchpad")])


def format_character_reason_prompt(initial_characters_summary: str, objective: str, other_guidelines: str, messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    return chat_prompt.format_messages(
        objective=objective,
        other_guidelines=other_guidelines,
        initial_characters_summary=initial_characters_summary,
        agent_scratchpad=messages,
    )

