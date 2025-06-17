"""Prompt utilities for the relationship agent."""

from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are 'RelationshipManagerAI', an expert in analyzing and updating relationships between characters in a narrative-driven game world. Using the available tools, progress step by step toward fulfilling the given objective.
"""

HUMAN_PROMPT = """
Below is all the information you need to complete your objective. Act accordingly.

## 1. The World Context
This is your **single initial source of truth** for the world's lore, tone, and context. ALL your actions and decisions must be deeply rooted in and consistent with this text. You must treat it as the project's "creative bible."

{narrative_context}

## 2. Supporting Information
This is additional or technical information that you must respect.

### Rules and Constraints:

This is your most important guiding principle: The Rule of 'Zero Assumed Context'. You must generate every piece of content as if the recipient has **ZERO prior knowledge** of the game world, its lore, or its rules. Do not take shortcuts or assume shared context. Everything should be self-contained and self-explanatory;
{relationship_rules_and_constraints}

### Other Guidelines (Softer rules):
{other_guidelines}

### Initial Summary The Relationships (if applicable):
{initial_relationship_summary}


## 3. Your Primary Objective
**{objective}**

You must achieve this objective in a way that honors and/or expands upon the world detailed in the Foundational Document above.

Begin your reasoning process now. 
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
