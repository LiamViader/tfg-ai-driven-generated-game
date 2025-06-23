
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from .schemas.graph_state import CharacterGraphState
from .prompts.reasoning import format_character_reason_prompt
from .tools.character_tools import EXECUTORTOOLS
from utils.message_window import get_valid_messages_window
from simulated.game_state import SimulatedGameStateSingleton

def receive_objective_node(state: CharacterGraphState) -> CharacterGraphState:
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    state.messages_field_to_update = "characters_executor_messages"
    state.logs_field_to_update = "characters_executor_applied_operations_log"
    state.characters_current_executor_iteration = 0
    state.characters_initial_summary = SimulatedGameStateSingleton.get_instance().simulated_characters.get_initial_summary()
    return state


def character_executor_reason_node(state: CharacterGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")
    llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")
    full_prompt = format_character_reason_prompt(
        initial_characters_summary=state.characters_initial_summary,
        objective=state.characters_current_objective,
        other_guidelines=state.characters_other_guidelines,
        messages=get_valid_messages_window(state.characters_executor_messages, 30),
        narrative_context=state.characters_global_narrative_context,
        character_rules_and_constraints=state.characters_rules_and_constraints,
    )
    state.characters_current_executor_iteration += 1
    response = llm.invoke(full_prompt)
    return {
        "characters_executor_messages": [response],
        "characters_current_executor_iteration": state.characters_current_executor_iteration,
    }


character_executor_tool_node = ToolNode(EXECUTORTOOLS)
character_executor_tool_node.messages_key = "characters_executor_messages"

