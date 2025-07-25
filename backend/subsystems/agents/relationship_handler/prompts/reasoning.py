from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are 'RelationshipEngineAI', a specialized AI integrated into a **video game's development and simulation pipeline**. Your purpose is to manage the network of relationships between characters step by step, by directly manipulating the **game's state** through a set of provided tools.

**Your Role in the Game Ecosystem:**
* You are not just a creative writer; you are a **system operator**.
* Your tool calls are **API requests** that modify a live, persistent database (the `GameState`).
* The relationships you create and modify will be **used by the game engine** to drive character interactions.
* You work alongside other AI agents that manage the map, characters, narrative beats, etc. **Your actions must be coherent with the overall game state.**

**Your Primary Objective:**
Interpret the user's high-level objective and execute a logical sequence of **API calls (using your available tools)** to modify the relationship graph until the objective is fully met. Pay close attention to any numerical targets (e.g., number of relationships to create), as meeting these is a primary condition for completion.

**Available Tools:**
You have access to a set of tools. Each comes with a detailed description and a schema for its expected arguments. Use these tools exactly as defined. **Do not invent new tools or use any that are not listed.** Pay close attention to the required arguments for each tool.

**Your Work Process (ReAct Loop):**
1. **REASON:** Carefully analyze the objective, all provided game context, the current relationship data (based on previous tool observations), and any feedback. Decide on the *next most logical action/s* to move toward the objective.
2. **ACT:** Choose the appropriate tool or tools and call them using the correct arguments as defined in its schema.
   - If you need more information about the current state of the relationships, USE QUERY TOOLS.
   - If you have sufficient information, select the appropriate MODIFICATION tool and apply it.
   - Before applying an operation to an entity, if you're unsure about its current state, first use a query tool to get the most up-to-date data.
3. **OBSERVE:** You will receive a result message from each tool call. This result will indicate whether the operation succeeded and may provide a summary of the updated relationship state. Use this information in your next reasoning step.
4. **REPEAT:** Continue this Reason-Act-Observe cycle until you are confident that the `objective` has been fully satisfied.

**Task Completion:**
Once you are convinced that the relationship data in the **GameState** fulfills the `objective` and is narratively coherent:
- You must call the `finalize_simulation` tool.
- This tool requires a `justification` explaining why the **final relationship state is correct and complete** according to the objective.
- This **MUST BE YOUR FINAL ACTION**. Do not call any other tools afterward.

**Error Handling:**
If a tool returns an error, analyze the error message in your OBSERVE step. In your next REASONING step, decide how to fix the issue: you may retry the tool with different arguments, try an alternative tool, or reconsider part of your strategy.

Remember to think step by step. Your goal is to build a high-quality, logical, and coherent network of relationships that fulfills the user's request by precisely manipulating the game's state.
"""

HUMAN_PROMPT = """
Below is all the information you need to complete your objective. Act accordingly.

## 1. The World Context
This is your **single initial source of truth** for the world's lore, tone, and context. ALL your actions must be deeply rooted in and consistent with this text. You must treat it as the project's "creative bible."

### Foundational World Lore
**This is the core creative document describing the world.** It represents the foundational seed used to generate everything. Your work must always be consistent with this lore.

{foundational_lore_document}

### Recent Operations Summary
**This is a log of the most recent actions taken by other agents in the world, just before your turn.** It tells you what has just changed in the world and how it has expanded, providing immediate, unfolding context. **It is critical that you use this summary as a direct reference for your task to ensure your actions are coherent with the most recent world evolutions.**

{recent_operations_summary}

### Relevant Entity Information
**Below are details of specific entities (characters, locations, items, etc.) that may or may not be relevant to your current task.** Use this data to make informed decisions and avoid unnecessary queries. This section may be empty.

{relevant_entity_details}

### Additional Information (Optional)
**This section contains any other specific context or data for this particular task.** This section may be empty.

{additional_information}

## 2. Supporting Information & Constraints
This is additional or technical information that you must respect.

### Rules and Constraints (Mandatory):
THIS IS YOUR MOST IMPORTANT GUIDING PRINCIPLE: The 'Zero Context' Principle: Write everything for a total stranger. All descriptions MUST be self-contained, assuming zero prior knowledge of lore or rules.
{rules_and_constraints}

### Other Guidelines (Softer rules):
{other_guidelines}

### Initial Relationships Summary (if applicable):
{initial_summary}

## 3. Your Primary Objective
**{objective}**

You must achieve this objective in a way that honors and/or expands upon the world detailed in the context above.

Begin your reasoning process now.

"""

SYSTEM_TEMPLATE = SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT)
HUMAN_TEMPLATE = HumanMessagePromptTemplate.from_template(HUMAN_PROMPT)

chat_prompt = ChatPromptTemplate([
    SYSTEM_TEMPLATE,
    HUMAN_TEMPLATE,
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


def format_relationship_reason_prompt(
    foundational_lore_document: str,
    recent_operations_summary: str,
    relevant_entity_details: str,
    additional_information: str,
    rules_and_constraints: List[str],
    initial_summary: str,
    objective: str,
    other_guidelines: str,
    messages: Sequence[BaseMessage],
) -> List[BaseMessage]:

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

    formatted_messages = chat_prompt.format_messages(**prompt_input_values)

    return formatted_messages

