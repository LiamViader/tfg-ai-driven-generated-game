from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence
from .schemas.graph_state import NarrativeGraphState
from .tools.narrative_tools import EXECUTORTOOLS, VALIDATIONTOOLS, finalize_simulation, validate_simulated_narrative
from .prompts.reasoning import format_narrative_react_reason_prompt
from .prompts.validating import format_narrative_react_validation_prompt
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.logs import ToolLog

NODE_WEIGHTS = {
    "narrative_executor_reason_node": 0.7,
    "narrative_validation_reason_node": 0.3,
}


def receive_objective_node(state: NarrativeGraphState):
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    SimulatedGameStateSingleton.begin_transaction()
    initial_summary = (
        SimulatedGameStateSingleton.get_instance().read_only_narrative.get_initial_summary()
    )
    return {
        "narrative_current_try": 0,
        "messages_field_to_update": "narrative_executor_messages",
        "logs_field_to_update": "narrative_executor_applied_operations_log",
        "narrative_current_executor_iteration": 0,
        "narrative_initial_summary": initial_summary,
        "narrative_executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "narrative_task_finalized_by_agent": False,
        "narrative_task_finalized_justification": None,
        "narrative_current_validation_iteration": 0,
        "narrative_task_succeeded_final": False,
    }

executor_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

def narrative_executor_reason_node(state: NarrativeGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")

    if state.narrative_progress_tracker is not None:
        max_iterations = state.narrative_max_executor_iterations
        weight_by_retry = NODE_WEIGHTS["narrative_executor_reason_node"] / (
            state.narrative_max_retries + 1
        )
        progress = weight_by_retry * (
            state.narrative_current_try
            + (state.narrative_current_executor_iteration / max_iterations)
        )
        state.narrative_progress_tracker.update(
            progress, "Generating/Updating narrative"
        )

    full_prompt = format_narrative_react_reason_prompt(
        foundational_lore_document=state.narrative_foundational_lore_document,
        recent_operations_summary=state.narrative_recent_operations_summary,
        relevant_entity_details=state.narrative_relevant_entity_details,
        additional_information=state.narrative_additional_information,
        rules_and_constraints=state.narrative_rules_and_constraints,
        initial_summary=state.narrative_initial_summary,
        objective=state.narrative_current_objective,
        other_guidelines=state.narrative_other_guidelines,
        messages=get_valid_messages_window(state.narrative_executor_messages, 30),
    )
    state.narrative_current_executor_iteration += 1
    response = executor_llm.invoke(full_prompt)
    return {
        "narrative_executor_messages": [response],
        "narrative_current_executor_iteration": state.narrative_current_executor_iteration,
    }

narrative_executor_tool_node = ToolNode(EXECUTORTOOLS)
narrative_executor_tool_node.messages_key = "narrative_executor_messages"


def receive_result_for_validation_node(state: NarrativeGraphState):
    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_logs(operation_logs: Sequence[ToolLog]) -> str:
        final_str = ""
        for operation in operation_logs:
            if operation.success and not operation.is_query:
                final_str += f"Result of '{operation.tool_called}': {operation.message}\n"
        return final_str

    return {
        "narrative_validation_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "messages_field_to_update": "narrative_validation_messages",
        "narrative_executor_agent_relevant_logs": format_relevant_logs(state.narrative_executor_applied_operations_log),
        "logs_field_to_update": "narrative_validator_applied_operations_log",
        "narrative_agent_validated": False,
        "narrative_agent_validation_conclusion_flag": False,
        "narrative_agent_validation_assessment_reasoning": "",
        "narrative_agent_validation_suggested_improvements": "",
        "narrative_current_validation_iteration": 0,
    }


def narrative_validation_reason_node(state: NarrativeGraphState):
    print("---ENTERING: REASON VALIDATION NODE---")

    if state.narrative_progress_tracker is not None:
        max_iterations = state.narrative_max_validation_iterations
        weight_by_retry = NODE_WEIGHTS["narrative_validation_reason_node"] / (
            state.narrative_max_retries + 1
        )
        progress = weight_by_retry * (
            state.narrative_current_try
            + (state.narrative_current_validation_iteration / max_iterations)
        )
        state.narrative_progress_tracker.update(
            NODE_WEIGHTS["narrative_executor_reason_node"] + progress,
            "Validating narrative",
        )
    state.narrative_current_validation_iteration += 1
    validation_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(VALIDATIONTOOLS, tool_choice="any")
    full_prompt = format_narrative_react_validation_prompt(
        state.narrative_current_objective,
        state.narrative_executor_agent_relevant_logs,
        state.narrative_validation_messages,
    )
    response = validation_llm.invoke(full_prompt)
    return {
        "narrative_validation_messages": [response],
        "narrative_current_validation_iteration": state.narrative_current_validation_iteration,
    }

narrative_validation_tool_node = ToolNode(VALIDATIONTOOLS)
narrative_validation_tool_node.messages_key = "narrative_validation_messages"


def retry_executor_node(state: NarrativeGraphState):
    print("---ENTERING: RETRY NODE---")
    feedback = (
        "Here's some human feedback on how you have done so far on your task:\n"
        f"You have still not completed your task\n Reason: {state.narrative_agent_validation_assessment_reasoning}\n"
        f"Suggestion/s:{state.narrative_agent_validation_suggested_improvements} "
    )
    feedback_message = HumanMessage(feedback)
    return {
        "narrative_executor_messages": [feedback_message],
        "messages_field_to_update": "narrative_executor_messages",
        "logs_field_to_update": "narrative_executor_applied_operations_log",
        "narrative_current_executor_iteration": 0,
        "narrative_current_try": state.narrative_current_try + 1,
    }


def final_node_success(state: NarrativeGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE SUCCESS---")
    SimulatedGameStateSingleton.commit()
    if state.narrative_progress_tracker is not None:
        state.narrative_progress_tracker.update(
            1.0, "Narrative task finalized successfully"
        )
    return {
        "narrative_task_succeeded_final": True,
    }


def final_node_failure(state: NarrativeGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")
    SimulatedGameStateSingleton.rollback()
    if state.narrative_progress_tracker is not None:
        state.narrative_progress_tracker.update(
            1.0, "Narrative task finalized successfully"
        )
    return {
        "narrative_task_succeeded_final": False,
    }
