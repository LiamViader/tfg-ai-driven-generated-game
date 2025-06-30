from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are 'RelationshipEngineAI', an AI agent responsible for managing the relationships between characters in a game's world. You operate by calling tools that directly modify the relationship data.
Follow the objective carefully and reason step by step before invoking any tool.
"""

HUMAN_PROMPT = """
World context and additional information is provided below. Use it to fulfil the objective.

Foundational Lore:
{foundational_lore_document}

Recent Operations Summary:
{recent_operations_summary}

Relevant Entity Details:
{relevant_entity_details}

Additional Information:
{additional_information}

Rules and Constraints:
{rules_and_constraints}

Initial Relationships Summary:
{initial_summary}

Objective:
{objective}
"""

SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)
chat_prompt = ChatPromptTemplate([SYSTEM_TEMPLATE, HUMAN_TEMPLATE, MessagesPlaceholder(variable_name="agent_scratchpad")])

def format_relationship_reason_prompt(foundational_lore_document: str, recent_operations_summary: str, relevant_entity_details: str, additional_information: str, rules_and_constraints: List[str], initial_summary: str, objective: str, other_guidelines: str, messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    prompt_input_values = {
        "foundational_lore_document": foundational_lore_document,
        "recent_operations_summary": recent_operations_summary,
        "relevant_entity_details": relevant_entity_details,
        "additional_information": additional_information,
        "rules_and_constraints": "; ".join(rules_and_constraints),
        "initial_summary": initial_summary,
        "objective": objective,
        "other_guidelines": other_guidelines,
        "agent_scratchpad": messages,
    }
    return chat_prompt.format_messages(**prompt_input_values)
