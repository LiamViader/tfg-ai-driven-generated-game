from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import ToolNode
from typing import Sequence, Dict, Any, List
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.agents.map_handler.tools.map_tools import EXECUTORTOOLS, VALIDATIONTOOLS, QUERYTOOLS, validate_simulated_map
from subsystems.agents.map_handler.prompts.reasoning import format_map_react_reason_prompt
from subsystems.agents.map_handler.prompts.validating import format_map_react_validation_prompt
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage, AIMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from simulated.game_state import SimulatedGameStateSingleton

from subsystems.agents.utils.logs import ToolLog

def receive_objective_node(state: MapGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    initial_summary=SimulatedGameStateSingleton.get_instance().simulated_map.get_summary_list()
    return {
        "map_current_try": 0,
        "messages_field_to_update": "map_executor_messages",
        "logs_field_to_update": "map_executor_applied_operations_log",
        "map_current_executor_iteration": 0,
        "map_initial_summary": initial_summary
    }


def map_executor_reason_node(state: MapGraphState):
    """
    Reasoning node. The llm requests the tool towards the next step
    """

    print("---ENTERING: REASON EXECUTION NODE---")
    map_reason_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

    full_prompt = format_map_react_reason_prompt(
        narrative_context=state.map_global_narrative_context,
        map_rules_and_constraints=state.map_rules_and_constraints,
        initial_map_summary=state.map_initial_summary,
        objective=state.map_current_objective,
        other_guidelines=state.map_other_guidelines,
        messages=get_valid_messages_window(state.map_executor_messages,30)
    )
    state.map_current_executor_iteration+=1

    print("CURRENT EXECUTOR ITERATION:", state.map_current_executor_iteration)
    
    response = map_reason_llm.invoke(full_prompt)

    return {
        "map_executor_messages": [response],
        "map_current_executor_iteration": state.map_current_executor_iteration
    }

map_executor_tool_node = ToolNode(EXECUTORTOOLS)
map_executor_tool_node.messages_key="map_executor_messages"


def receive_result_for_validation_node(state: MapGraphState):
    """
    Intermidiate step between the execution of the simulated map and the validation
    """

    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_executing_agent_logs(operation_logs: Sequence[ToolLog])->str:
        final_str = ""
        for operation in operation_logs:
            if operation.success:
                if not operation.is_query:
                    final_str += f"Result of '{operation.tool_called}': {operation.message}\n"
        return final_str


    return {
        "map_validation_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "messages_field_to_update": "map_validation_messages",
        "map_executor_agent_relevant_logs": format_relevant_executing_agent_logs(state.map_executor_applied_operations_log),
        "logs_field_to_update": "map_validator_applied_operations_log",
        "map_agent_validated": False,
        "map_current_validation_iteration": 0
    }

def map_validation_reason_node(state: MapGraphState):
    """
    Reasoning validation node. The llm requests the tool querys and validates when has enought information or maxvalidation iteration is exceeded
    """
    print("---ENTERING: REASON VALIDATION NODE---")

    state.map_current_validation_iteration+=1
    if state.map_current_validation_iteration <= state.map_max_validation_iterations:
        map_validation_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools(VALIDATIONTOOLS, tool_choice="any")
    else:
        map_validation_llm = ChatOpenAI(model="gpt-4.1-mini",).bind_tools([validate_simulated_map], tool_choice="any")
    
    full_prompt=format_map_react_validation_prompt(
        state.map_current_objective,
        state.map_executor_agent_relevant_logs,
        state.map_validation_messages
    )
    print("CURRENT VALIDATION ITERATION:", state.map_current_validation_iteration)
    response = map_validation_llm.invoke(full_prompt)
    return {
        "map_validation_messages": [response],
        "map_current_validation_iteration": state.map_current_validation_iteration
    }

map_validation_tool_node = ToolNode(VALIDATIONTOOLS)
map_validation_tool_node.messages_key="map_validation_messages"

def retry_executor_node(state: MapGraphState):
    """
    Serves as an intermidiate step between the validation and a new execution retry. Adds the feedback from the last validation.
    """

    print("---ENTERING: RETRY NODE---")


    feedback = f"Here's some human feedback on how you have done so far on your task:\n You have still not completed your task\n Reason: {state.map_agent_validation_assessment_reasoning}\n Suggestion/s:{state.map_agent_validation_suggested_improvements} "
    
    feedback_message = HumanMessage(feedback)

    return {
        "map_executor_messages": [feedback_message],
        "messages_field_to_update": "map_executor_messages",
        "logs_field_to_update": "map_executor_applied_operations_log",
        "map_current_executor_iteration": 0,
        "map_current_try": state.map_current_try+1
    }

def last_node_success(state: MapGraphState) -> MapGraphState:
    """
    Last node of agent if succeeded on objective.
    """
    print("---ENTERING: LAST NODE OBJECTIVE SUCESS---")

    return state

def last_node_failed(state: MapGraphState) -> MapGraphState:
    """
    Last node of agent if failed on objective.
    """
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")

    return state