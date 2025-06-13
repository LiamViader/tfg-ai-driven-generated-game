from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are a Narrative Design Assistant. Choose the most appropriate narrative structure type for the story.
You may use tools to inspect the available structures before making your decision.
When sure, call `select_narrative_structure` with the id of your choice.
Available structures: {structure_names}
"""

HUMAN_PROMPT = """
Refined prompt:
{refined_prompt}
Main goal: {main_goal}
"""

system_template = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
human_template = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt_template = ChatPromptTemplate([
    system_template,
    human_template,
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

def format_structure_selection_prompt(refined_prompt: str, main_goal: str, structure_names: str, messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    prompt_values = {
        "refined_prompt": refined_prompt,
        "main_goal": main_goal,
        "structure_names": structure_names,
        "agent_scratchpad": messages,
    }
    return chat_prompt_template.format_messages(**prompt_values)
