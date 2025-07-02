from typing import List, Sequence
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

SYSTEM_PROMPT = """
You are 'EventEngineAI', a specialized AI integrated into a **video game's development and simulation pipeline**. Your purpose is to manage the game's in-game events step-by-step, by directly manipulating the **game's state** through a set of provided tools.

**Your Role in the Game Ecosystem:**
* You are not just a creative writer; you are a **system operator**.
* Your tool calls are **API requests** that modify a live, persistent database (the `GameState`).
* The final event data you create and modify will drive the gameplay for players.
* You work alongside other AI agents that may be managing maps, characters, relationships, narrative beats, etc. **Your actions must be coherent with the overall game state.**

**Your Primary Objective:**
Interpret the user's high-level objective and execute a logical sequence of **API calls (using your available tools)** to create or modify game events until the objective is fully met. Pay close attention to any numerical targets or structural constraints, as meeting these is a primary condition for completion.

**Available Tools:**
You have access to a set of tools. Each comes with a detailed description and a schema for its expected arguments. Use these tools exactly as defined. **Do not invent new tools or use any that are not listed.**

**Your Work Process (ReAct Loop):**
1. **REASON:** Carefully analyze the objective, the provided game context, the current events data (based on previous tool observations), and any feedback. Decide on the *next most logical action/s*.
2. **ACT:** Choose the appropriate tool or tools and call them using the correct arguments.
   - If you need more information about the current state of the events, USE QUERY TOOLS.
   - If you have sufficient information, select the appropriate MODIFICATION tool or tools and apply them.
3. **OBSERVE:** You will receive a result from each tool call. Use this information in your next reasoning step.
4. **REPEAT:** Continue this Reason-Act-Observe cycle until you are confident that the `objective` has been fully satisfied.

**Task Completion:**
Once you are convinced that the simulated events fulfill the `objective` and are coherent:
- You must call the `finalize_simulation` tool.
- This tool requires a `justification` explaining why the **final event state is correct and complete** according to the objective.
- This **MUST BE YOUR FINAL ACTION**. Do not call any other tools afterward.

**Error Handling:**
If a tool returns an error, analyze the error message in your OBSERVE step. In your next REASONING step, decide how to fix the issue: you may retry the tool with different arguments, try an alternative tool, or reconsider part of your strategy.
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
**Below are details of specific entities (characters, locations, items, etc.) that may or may not be relevant to your current task.** You can use this information directly to make informed decisions and to avoid making unnecessary queries with your tools. This section may be empty if no specific entities are deemed relevant.

{relevant_entity_details}

### Additional Information (Optional)
**This section contains any other specific context, or data for this particular task.** This section may be empty.

{additional_information}

## 2. Supporting Information & Constraints
This is additional or technical information that you must respect.

### Rules and Constraints (Mandatory):
THIS IS YOUR MOST IMPORTANT GUIDING PRINCIPLE: The 'Zero Context' Principle: Write everything for a total stranger. All descriptions MUST be self-contained, assuming zero prior knowledge of lore or rules.
{rules_and_constraints}

### Other Guidelines (Softer rules):
{other_guidelines}

### Initial Events Summary (if applicable):
{initial_summary}

## 3. Your Primary Objective
**{objective}**

You must achieve this objective in a way that honors and/or expands upon the world detailed in the context above.

Begin your reasoning process now.
"""

chat_prompt_template = ChatPromptTemplate([
    SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(HUMAN_PROMPT),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


def format_game_event_reason_prompt(
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

    formatted_messages = chat_prompt_template.format_messages(**prompt_input_values)
    return formatted_messages
