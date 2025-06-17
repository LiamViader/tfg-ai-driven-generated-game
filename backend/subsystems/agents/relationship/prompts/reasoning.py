"""Prompt utilities for the relationship agent."""

from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are 'RelationshipManagerAI', an expert in analyzing and updating relationships between characters in a narrative-driven game world. Using the available tools, progress step by step toward fulfilling the given objective.
"""

HUMAN_PROMPT = """
World Context:
{narrative_context}

Rules and Constraints:
{relationship_rules_and_constraints}

Other Guidelines:
{other_guidelines}

Initial Relationships Summary:
{initial_relationships_summary}

Objective:
**{objective}**

Begin your reasoning now.
"""

SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt = ChatPromptTemplate([SYSTEM_TEMPLATE, HUMAN_TEMPLATE, MessagesPlaceholder(variable_name="agent_scratchpad")])


def format_relationship_reason_prompt(narrative_context: str, relationship_rules_and_constraints: List[str], initial_relationships_summary: str, objective: str, other_guidelines: str, messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    return chat_prompt.format_messages(
        narrative_context=narrative_context,
        relationship_rules_and_constraints="; ".join(relationship_rules_and_constraints),
        initial_relationships_summary=initial_relationships_summary,
        objective=objective,
        other_guidelines=other_guidelines,
        agent_scratchpad=messages,
    )
