from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from typing import List, Sequence

SYSTEM_PROMPT = """
You are the validation phase of the RelationshipEngineAI. Evaluate whether the relationships created fulfill the given objective. Provide reasoning and suggest improvements if necessary.
"""

HUMAN_PROMPT = """
Objective: {objective}

Executor Agent Logs:
{executor_logs}

Previous messages:
{validation_messages}
"""

SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)
chat_prompt = ChatPromptTemplate([SYSTEM_TEMPLATE, HUMAN_TEMPLATE, MessagesPlaceholder(variable_name="agent_scratchpad")])

def format_relationship_validation_prompt(objective: str, executor_logs: str, validation_messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    prompt_input_values = {
        "objective": objective,
        "executor_logs": executor_logs,
        "validation_messages": validation_messages,
        "agent_scratchpad": [],
    }
    return chat_prompt.format_messages(**prompt_input_values)
