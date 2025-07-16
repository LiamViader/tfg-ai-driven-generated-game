from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence

from .schemas.graph_state import GameEventGraphState
from .prompts.reasoning import format_game_event_reason_prompt
from .prompts.validating import format_game_event_validation_prompt
from .tools.event_tools import EXECUTORTOOLS, VALIDATIONTOOLS, validate_simulated_game_events
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.logs import ToolLog

NODE_WEIGHTS = {
    "game_event_executor_reason_node": 0.7,
    "game_event_validation_reason_node": 0.3,
}


def receive_objective_node(state: GameEventGraphState):
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    SimulatedGameStateSingleton.begin_transaction()
    initial_summary = SimulatedGameStateSingleton.get_instance().read_only_events.get_initial_summary()
    return {
        "events_current_try": 0,
        "messages_field_to_update": "events_executor_messages",
        "logs_field_to_update": "events_executor_applied_operations_log",
        "events_current_executor_iteration": 0,
        "events_initial_summary": initial_summary,
        "events_executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "events_task_finalized_by_agent": False,
        "events_task_finalized_justification": None,
        "events_current_validation_iteration": 0,
        "events_task_succeeded_final": False,
    }

executor_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

def game_event_executor_reason_node(state: GameEventGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")

    if state.events_progress_tracker is not None:
        max_retries = state.events_max_retries + 1
        max_iterations = state.events_max_executor_iterations or 1
        progress_from_previous_tries = state.events_current_try / max_retries
        weight_of_current_try_block = 1 / max_retries
        progress_within_execution_phase = (
            state.events_current_executor_iteration / max_iterations
        )
        current_phase_progress = (
            progress_within_execution_phase
            * weight_of_current_try_block
            * NODE_WEIGHTS["game_event_executor_reason_node"]
        )
        total_local_progress = progress_from_previous_tries + current_phase_progress
        state.events_progress_tracker.update(
            total_local_progress, "Generating/Updating events"
        )

    full_prompt = format_game_event_reason_prompt(
        foundational_lore_document=state.events_foundational_lore_document,
        recent_operations_summary=state.events_recent_operations_summary,
        relevant_entity_details=state.events_relevant_entity_details,
        additional_information=state.events_additional_information,
        rules_and_constraints=state.events_rules_and_constraints,
        initial_summary=state.events_initial_summary,
        objective=state.events_current_objective,
        other_guidelines=state.events_other_guidelines,
        messages=get_valid_messages_window(state.events_executor_messages, 30),
    )
    state.events_current_executor_iteration += 1
    response = executor_llm.invoke(full_prompt)
    return {
        "events_executor_messages": [response],
        "events_current_executor_iteration": state.events_current_executor_iteration,
    }


game_event_executor_tool_node = ToolNode(EXECUTORTOOLS)
game_event_executor_tool_node.messages_key = "events_executor_messages"


def receive_result_for_validation_node(state: GameEventGraphState):
    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_logs(operation_logs: Sequence[ToolLog]) -> str:
        final_str = ""
        for operation in operation_logs:
            if operation.success and not operation.is_query:
                final_str += f"Result of '{operation.tool_called}': {operation.message}\n"
        return final_str

    return {
        "events_validation_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "messages_field_to_update": "events_validation_messages",
        "events_executor_agent_relevant_logs": format_relevant_logs(state.events_executor_applied_operations_log),
        "logs_field_to_update": "events_validator_applied_operations_log",
        "events_agent_validated": False,
        "events_agent_validation_conclusion_flag": False,
        "events_agent_validation_assessment_reasoning": "",
        "events_agent_validation_suggested_improvements": "",
        "events_current_validation_iteration": 0,
    }


def game_event_validation_reason_node(state: GameEventGraphState):
    print("---ENTERING: REASON VALIDATION NODE---")

    if state.events_progress_tracker is not None:
        max_retries = state.events_max_retries + 1
        max_iterations = state.events_max_validation_iterations + 1 or 1
        progress_from_completed_tries = state.events_current_try / max_retries
        weight_of_current_try_block = 1 / max_retries
        progress_from_this_try_execution = (
            weight_of_current_try_block * NODE_WEIGHTS["game_event_executor_reason_node"]
        )
        progress_within_validation_phase = (
            state.events_current_validation_iteration / max_iterations
        )
        progress_from_this_try_validation = (
            progress_within_validation_phase
            * weight_of_current_try_block
            * NODE_WEIGHTS["game_event_validation_reason_node"]
        )
        total_local_progress = (
            progress_from_completed_tries
            + progress_from_this_try_execution
            + progress_from_this_try_validation
        )
        state.events_progress_tracker.update(
            total_local_progress,
            "Validating events",
        )
    state.events_current_validation_iteration += 1
    if state.events_current_validation_iteration <= state.events_max_validation_iterations:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(VALIDATIONTOOLS, tool_choice="any")
    else:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools([validate_simulated_game_events], tool_choice="any")
    full_prompt = format_game_event_validation_prompt(
        state.events_current_objective,
        state.events_executor_agent_relevant_logs,
        state.events_validation_messages,
    )
    response = validation_llm.invoke(full_prompt)
    return {
        "events_validation_messages": [response],
        "events_current_validation_iteration": state.events_current_validation_iteration,
    }


game_event_validation_tool_node = ToolNode(VALIDATIONTOOLS)
game_event_validation_tool_node.messages_key = "events_validation_messages"


def retry_executor_node(state: GameEventGraphState):
    print("---ENTERING: RETRY NODE---")
    feedback = (
        "Here's some human feedback on how you have done so far on your task:\n"
        "You have still not completed your task\n Reason: "
        f"{state.events_agent_validation_assessment_reasoning}\n Suggestion/s:{state.events_agent_validation_suggested_improvements} "
    )
    feedback_message = HumanMessage(feedback)
    return {
        "events_executor_messages": [feedback_message],
        "messages_field_to_update": "events_executor_messages",
        "logs_field_to_update": "events_executor_applied_operations_log",
        "events_current_executor_iteration": 0,
        "events_current_try": state.events_current_try + 1,
    }


def final_node_success(state: GameEventGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE SUCCESS---")
    SimulatedGameStateSingleton.commit()
    if state.events_progress_tracker is not None:
        state.events_progress_tracker.update(
            1.0, "Events task finalized successfully"
        )
    return {
        "events_task_succeeded_final": True,
    }


def final_node_failure(state: GameEventGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")
    SimulatedGameStateSingleton.rollback()
    if state.events_progress_tracker is not None:
        state.events_progress_tracker.update(
            1.0, "Events task finalized successfully"
        )
    return {
        "events_task_succeeded_final": False,
    }
