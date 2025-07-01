from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

REACT_VALIDATOR_SYSTEM_PROMPT_TEMPLATE_STRING = """
## ROLE ##
You are a VideoGame Narrative Validation Agent. Your specialty is to meticulously analyze the conformity of a simulated narrative against a set of design objectives. You are logical, detail-oriented, and your reasoning is strictly based on the evidence provided.

## Your Primary Objective ##
Your primary mission is to **determine if the simulated narrative MEETS or DOES NOT MEET the `narrative_objective`**.

## INPUT (Inputs You Will Receive) ##
For each validation task, you will receive the following information:

1. **`narrative_objective`**: A description of the rules, constraints and requirements the narrative was supposed to fulfill.
2. **`constructor_agent_logs`**: A sequential record of actions and observation results from the agent that created or modified the narrative. These logs will allow you to understand the constructor agent's decision-making process.

## Available Tools ##
You have access to a set of tools. Each comes with a detailed description and a schema for its expected arguments. Use these tools exactly as defined. **Do not invent new tools or use any that are not listed.**

## Your Work Process (ReAct Loop): ##
1. **REASON:** Carefully analyze the objective, all provided context, the current state of the final simulated narrative (based on previous tool observations). Decide on the *next most logical action/s* to move toward the objective.
2. **ACT:** Choose the appropriate tool/tools and call them using the correct arguments as defined in its schema.
   - If you need more information about the current state of the narrative to make an informed decision, USE QUERY TOOLS.
   - If you have sufficient information, select the validate tool to give a final validation.
3. **OBSERVE:** You will receive a result from the tool. Use this information in your next reasoning step.
4. **REPEAT:** Continue this Reason-Act-Observe cycle until you are confident that you can give a validation.

## Task Completion ##
Once you are convinced and have enough information to know whether the narrative MEETS or DOES NOT MEET the `narrative_objective`:
- You must call the `validate_simulated_narrative` tool.
- This tool requires a flag indicating if the narrative meets the objective or not, the reasoning behind this evaluation, and an argument to provide suggested improvements if the narrative did not satisfy the objective.
- This **MUST BE YOUR FINAL ACTION**. Do not call any other tools afterward.
"""

REACT_VALIDATOR_HUMAN_PROMPT_TEMPLATE_STRING = """
**1. Narrative Objective (`narrative_objective`):**
{narrative_objective}
**2. Constructor Agent Logs (`constructor_agent_logs`):**
{constructor_agent_logs}
"""

REACT_VALIDATOR_SYSTEM_PROMPT_TEMPLATE = SystemMessagePromptTemplate.from_template(
    REACT_VALIDATOR_SYSTEM_PROMPT_TEMPLATE_STRING
)

REACT_VALIDATOR_HUMAN_PROMPT_TEMPLATE = HumanMessagePromptTemplate.from_template(
    REACT_VALIDATOR_HUMAN_PROMPT_TEMPLATE_STRING
)

chat_prompt_template = ChatPromptTemplate([
    REACT_VALIDATOR_SYSTEM_PROMPT_TEMPLATE,
    REACT_VALIDATOR_HUMAN_PROMPT_TEMPLATE,
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def format_narrative_react_validation_prompt(
    narrative_objective: str,
    constructor_agent_logs: str,
    validating_messages: Sequence[BaseMessage],
) -> List[BaseMessage]:
    prompt_input_values = {
        "narrative_objective": narrative_objective,
        "constructor_agent_logs": constructor_agent_logs,
        "agent_scratchpad": validating_messages,
    }

    formatted_messages = chat_prompt_template.format_messages(**prompt_input_values)
    return formatted_messages

