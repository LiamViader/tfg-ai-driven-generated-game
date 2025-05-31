from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import ToolNode

from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.tools.map_executor_tools import TOOLS
from subsystems.map.prompts.map_reasoning_prompts import format_map_react_reason_prompt
from utils.message_window import get_valid_messages_window

def receive_objective_node(state: MapGraphState) -> MapGraphState:
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OBJECTIVE NODE---")

    state.reset_working_memory()


    return state


def map_reason_node(state: MapGraphState):
    """
    Reasoning node. The llm requests the tool towards the next step
    """


    print("---ENTERING: REASON EXECUTION NODE---")
    map_reason_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools(TOOLS, tool_choice="any")

    full_prompt = format_map_react_reason_prompt(
        narrative_context=state.global_narrative_context,
        map_rules_and_constraints=state.map_rules_and_constraints,
        initial_map_summary=state.initial_map_summary,
        previous_feedback=state.previous_feedback,
        objective=state.current_objective,
        other_guidelines=state.other_guidelines,
        messages=get_valid_messages_window(state.messages,30)
    )
    state.current_executor_iteration+=1
    print("CURRENT ITERATION:", state.current_executor_iteration)

    response = map_reason_llm.invoke(full_prompt)
    return {
        "messages": [response],
        "current_iteration": state.current_executor_iteration
    }

map_executor_node = ToolNode(TOOLS)

def receive_result_for_validation_node(state: MapGraphState):
    """
    Intermidiate step between the execution of the simulated map and the validation
    """
    state.working_simulated_map.executor_or_validator = "validator"
    return {
        "working_simulated_map": state.working_simulated_map
    }

def map_validation_reason_node(state: MapGraphState):
    """
    Reasoning validation node. The llm requests the tool querys and validates when has enought information or maxvalidation iteration is exceeded
    """


    print("---ENTERING: REASON VALIDATION NODE---")
    
    map_validation_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools(TOOLS, tool_choice="any")
    state.working_simulated_map.executor_or_validator = "validator"