
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence

from .schemas.graph_state import CharacterGraphState
from .prompts.reasoning import format_character_reason_prompt
from .prompts.validating import format_character_validation_prompt
from .tools.character_tools import EXECUTORTOOLS, VALIDATIONTOOLS, validate_simulated_characters
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.logs import ToolLog
import httpx



NODE_WEIGHTS = {
    "character_executor_reason_node": 0.7,
    "character_validation_reason_node": 0.3,
}

def receive_objective_node(state: CharacterGraphState):
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    SimulatedGameStateSingleton.begin_transaction()
    initial_summary = SimulatedGameStateSingleton.get_instance().read_only_characters.get_initial_summary()
    return {
        "characters_current_try": 0,
        "messages_field_to_update": "characters_executor_messages",
        "logs_field_to_update": "characters_executor_applied_operations_log",
        "characters_current_executor_iteration": 0,
        "characters_initial_summary": initial_summary,
        "characters_executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "characters_task_finalized_by_agent": False,
        "characters_task_finalized_justification": None,
        "characters_current_validation_iteration": 0,
        "characters_task_succeeded_final": False,
    }

timeout_executor = httpx.Timeout(None)
executor_llm = ChatOpenAI(model="gpt-4.1-mini", timeout=timeout_executor).bind_tools(EXECUTORTOOLS, tool_choice="any")

def character_executor_reason_node(state: CharacterGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")

    if state.characters_progress_tracker is not None:
        max_retries = state.characters_max_retries + 1
        max_iterations = state.characters_max_executor_iterations or 1
        progress_from_previous_tries = state.characters_current_try / max_retries
        weight_of_current_try_block = 1 / max_retries
        progress_within_execution_phase = (
            state.characters_current_executor_iteration / max_iterations
        )
        current_phase_progress = (
            progress_within_execution_phase
            * weight_of_current_try_block
            * NODE_WEIGHTS["character_executor_reason_node"]
        )
        total_local_progress = progress_from_previous_tries + current_phase_progress
        state.characters_progress_tracker.update(
            total_local_progress, "Generating/Updating characters"
        )

    print("TOOLS BINDED")
    full_prompt = format_character_reason_prompt(
        foundational_lore_document=state.characters_foundational_lore_document,
        recent_operations_summary=state.characters_recent_operations_summary,
        relevant_entity_details=state.characters_relevant_entity_details,
        additional_information=state.characters_additional_information,
        rules_and_constraints=state.characters_rules_and_constraints,
        initial_summary=state.characters_initial_summary,
        objective=state.characters_current_objective,
        other_guidelines=state.characters_other_guidelines,
        messages=get_valid_messages_window(state.characters_executor_messages, 30),
    )
    print("PROMPT FORMATED")
    state.characters_current_executor_iteration += 1
    response = executor_llm.invoke(full_prompt)
    print("LLM INVOKED")
    return {
        "characters_executor_messages": [response],
        "characters_current_executor_iteration": state.characters_current_executor_iteration,
    }


character_executor_tool_node = ToolNode(EXECUTORTOOLS)
character_executor_tool_node.messages_key = "characters_executor_messages"


def receive_result_for_validation_node(state: CharacterGraphState):
    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_executing_agent_logs(operation_logs: Sequence[ToolLog]) -> str:
        final_str = ""
        for operation in operation_logs:
            if operation.success:
                if not operation.is_query:
                    final_str += f"Result of '{operation.tool_called}': {operation.message}\n"
        return final_str

    return {
        "characters_validation_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "messages_field_to_update": "characters_validation_messages",
        "characters_executor_agent_relevant_logs": format_relevant_executing_agent_logs(state.characters_executor_applied_operations_log),
        "logs_field_to_update": "characters_validator_applied_operations_log",
        "characters_agent_validated": False,
        "characters_agent_validation_conclusion_flag": False,
        "characters_agent_validation_assessment_reasoning": "",
        "characters_agent_validation_suggested_improvements": "",
        "characters_current_validation_iteration": 0,
    }


def character_validation_reason_node(state: CharacterGraphState):
    print("---ENTERING: REASON VALIDATION NODE---")

    if state.characters_progress_tracker is not None:
        max_retries = state.characters_max_retries + 1
        max_iterations = state.characters_max_validation_iterations + 1 or 1
        progress_from_completed_tries = state.characters_current_try / max_retries
        weight_of_current_try_block = 1 / max_retries
        progress_from_this_try_execution = (
            weight_of_current_try_block * NODE_WEIGHTS["character_executor_reason_node"]
        )
        progress_within_validation_phase = (
            state.characters_current_validation_iteration / max_iterations
        )
        progress_from_this_try_validation = (
            progress_within_validation_phase
            * weight_of_current_try_block
            * NODE_WEIGHTS["character_validation_reason_node"]
        )
        total_local_progress = (
            progress_from_completed_tries
            + progress_from_this_try_execution
            + progress_from_this_try_validation
        )
        state.characters_progress_tracker.update(
            total_local_progress,
            "Validating characters",
        )
    timeout_validation = httpx.Timeout(None)
    state.characters_current_validation_iteration += 1
    if state.characters_current_validation_iteration <= state.characters_max_validation_iterations:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini", timeout=timeout_validation).bind_tools(VALIDATIONTOOLS, tool_choice="any")
    else:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini", timeout=timeout_validation).bind_tools([validate_simulated_characters], tool_choice="any")

    full_prompt = format_character_validation_prompt(
        state.characters_current_objective,
        state.characters_executor_agent_relevant_logs,
        state.characters_validation_messages,
    )
    response = validation_llm.invoke(full_prompt)
    return {
        "characters_validation_messages": [response],
        "characters_current_validation_iteration": state.characters_current_validation_iteration,
    }


character_validation_tool_node = ToolNode(VALIDATIONTOOLS)
character_validation_tool_node.messages_key = "characters_validation_messages"


def retry_executor_node(state: CharacterGraphState):
    print("---ENTERING: RETRY NODE---")

    feedback = (
        "Here's some human feedback on how you have done so far on your task:\n "
        "You have still not completed your task\n Reason: "
        f"{state.characters_agent_validation_assessment_reasoning}\n Suggestion/s:{state.characters_agent_validation_suggested_improvements} "
    )

    feedback_message = HumanMessage(feedback)

    return {
        "characters_executor_messages": [feedback_message],
        "messages_field_to_update": "characters_executor_messages",
        "logs_field_to_update": "characters_executor_applied_operations_log",
        "characters_current_executor_iteration": 0,
        "characters_current_try": state.characters_current_try + 1,
    }


def final_node_success(state: CharacterGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE SUCCESS---")
    SimulatedGameStateSingleton.commit()
    if state.characters_progress_tracker is not None:
        state.characters_progress_tracker.update(
            1.0, "Characters task finalized successfully"
        )
    return {
        "characters_task_succeeded_final": True,
    }


def final_node_failure(state: CharacterGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")
    SimulatedGameStateSingleton.rollback()
    if state.characters_progress_tracker is not None:
        state.characters_progress_tracker.update(
            1.0, "Characters task finalized successfully"
        )
    return {
        "characters_task_succeeded_final": False,
    }

