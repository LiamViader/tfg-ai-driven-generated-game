from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import ToolNode
from typing import Sequence, Dict, Any, List
from subsystems.map.schemas.graph_state import MapGraphState
from subsystems.map.tools.map_tools import EXECUTORTOOLS, VALIDATIONTOOLS, QUERYTOOLS, validate_simulated_map
from subsystems.map.prompts.map_reasoning_prompts import format_map_react_reason_prompt
from subsystems.map.prompts.map_validation_prompts import format_map_react_validation_prompt
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage

def receive_objective_node(state: MapGraphState) -> MapGraphState:
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    state.reset_working_memory()
    return state


def map_executor_reason_node(state: MapGraphState):
    """
    Reasoning node. The llm requests the tool towards the next step
    """

    print("---ENTERING: REASON EXECUTION NODE---")
    map_reason_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

    full_prompt = format_map_react_reason_prompt(
        narrative_context=state.global_narrative_context,
        map_rules_and_constraints=state.map_rules_and_constraints,
        initial_map_summary=state.initial_map_summary,
        previous_feedback=state.previous_feedback,
        objective=state.current_objective,
        other_guidelines=state.other_guidelines,
        messages=get_valid_messages_window(state.executor_messages,30)
    )
    state.current_executor_iteration+=1
    print("CURRENT EXECUTOR ITERATION:", state.current_executor_iteration)

    response = map_reason_llm.invoke(full_prompt)
    return {
        "executor_messages": [response],
        "current_executor_iteration": state.current_executor_iteration
    }

map_executor_tool_node = ToolNode(EXECUTORTOOLS)
map_executor_tool_node.messages_key = "executor_messages"

def receive_result_for_validation_node(state: MapGraphState):
    """
    Intermidiate step between the execution of the simulated map and the validation
    """

    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_executing_agent_logs(operation_logs: List[Dict[str, Any]])->str:
        final_str = ""
        query_tool_names = [tool_function.name for tool_function in QUERYTOOLS]
        for operation in operation_logs:
            if operation["success"]:
                if operation["tool_called"] not in query_tool_names:
                    final_str += f"Result of '{operation["tool_called"]}': {operation["message"]}.\n"
        return final_str

    state.working_simulated_map.executor_or_validator = "validator"

    return {
        "working_simulated_map":  state.working_simulated_map,
        "current_validation_iteration": 0,
        "executor_agent_relevant_logs": format_relevant_executing_agent_logs(state.working_simulated_map.executor_applied_operations_log)
    }

def map_validation_reason_node(state: MapGraphState):
    """
    Reasoning validation node. The llm requests the tool querys and validates when has enought information or maxvalidation iteration is exceeded
    """

    print("---ENTERING: REASON VALIDATION NODE---")

    state.current_validation_iteration+=1
    if state.current_validation_iteration <= state.max_validation_iterations:
        map_validation_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools(VALIDATIONTOOLS, tool_choice="any")
    else:
        map_validation_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools([validate_simulated_map], tool_choice="any")
    
    full_prompt=format_map_react_validation_prompt(
        state.current_objective,
        state.executor_agent_relevant_logs,
        state.validation_messages
    )
    print("CURRENT VALIDATION ITERATION:", state.current_validation_iteration)
    response = map_validation_llm.invoke(full_prompt)
    return {
        "validation_messages": [response],
        "current_validation_iteration": state.current_validation_iteration
    }

map_validation_tool_node = ToolNode(VALIDATIONTOOLS)
map_validation_tool_node.messages_key = "validation_messages"