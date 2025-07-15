from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from typing import Sequence
from subsystems.agents.relationship_handler.schemas.graph_state import RelationshipGraphState
from subsystems.agents.relationship_handler.tools.relationship_tools import (
    EXECUTORTOOLS,
    VALIDATIONTOOLS,
    get_relationship_details,
    validate_simulated_relationships,
)
from subsystems.agents.relationship_handler.prompts.reasoning import format_relationship_reason_prompt
from subsystems.agents.relationship_handler.prompts.validating import format_relationship_validation_prompt
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from subsystems.agents.utils.logs import ToolLog

NODE_WEIGHTS = {
    "relationship_executor_reason_node": 0.7,
    "relationship_validation_reason_node": 0.3,
}
from simulated.singleton import SimulatedGameStateSingleton


def receive_objective_node(state: RelationshipGraphState):
    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    SimulatedGameStateSingleton.begin_transaction()
    initial_summary = SimulatedGameStateSingleton.get_instance().read_only_relationships.get_initial_summary()
    return {
        "relationships_current_try": 0,
        "messages_field_to_update": "relationships_executor_messages",
        "logs_field_to_update": "relationships_executor_applied_operations_log",
        "relationships_current_executor_iteration": 0,
        "relationships_initial_summary": initial_summary,
        "relationships_executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "relationships_task_finalized_by_agent": False,
        "relationships_task_finalized_justification": None,
        "relationships_current_validation_iteration": 0,
        "relationships_task_succeeded_final": False,
    }

executor_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

def relationship_executor_reason_node(state: RelationshipGraphState):
    print("---ENTERING: REASON EXECUTION NODE---")

    if state.relationships_progress_tracker is not None:
        max_iterations = state.relationships_max_executor_iterations
        weight_by_retry = NODE_WEIGHTS["relationship_executor_reason_node"] / (
            state.relationships_max_retries + 1
        )
        progress = weight_by_retry * (
            (state.relationships_current_try - 1)
            + (state.relationships_current_executor_iteration / max_iterations)
        )
        state.relationships_progress_tracker.update(
            progress, "Generating/Updating relationships"
        )

    full_prompt = format_relationship_reason_prompt(
        foundational_lore_document=state.relationships_foundational_lore_document,
        recent_operations_summary=state.relationships_recent_operations_summary,
        relevant_entity_details=state.relationships_relevant_entity_details,
        additional_information=state.relationships_additional_information,
        rules_and_constraints=state.relationships_rules_and_constraints,
        initial_summary=state.relationships_initial_summary,
        objective=state.relationships_current_objective,
        other_guidelines=state.relationships_other_guidelines,
        messages=get_valid_messages_window(state.relationships_executor_messages, 30),
    )
    state.relationships_current_executor_iteration += 1
    response = executor_llm.invoke(full_prompt)
    return {
        "relationships_executor_messages": [response],
        "relationships_current_executor_iteration": state.relationships_current_executor_iteration,
    }

relationship_executor_tool_node = ToolNode(EXECUTORTOOLS)
relationship_executor_tool_node.messages_key = "relationships_executor_messages"


def receive_result_for_validation_node(state: RelationshipGraphState):
    print("---ENTERING: RECEIVE RESULT FOR VALIDATION NODE---")

    def format_relevant_logs(operation_logs: Sequence[ToolLog]) -> str:
        final_str = ""
        for operation in operation_logs:
            if operation.success:
                if not operation.is_query:
                    final_str += f"Result of '{operation.tool_called}': {operation.message}\n"
        return final_str

    return {
        "relationships_validation_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "messages_field_to_update": "relationships_validation_messages",
        "relationships_executor_agent_relevant_logs": format_relevant_logs(state.relationships_executor_applied_operations_log),
        "logs_field_to_update": "relationships_validator_applied_operations_log",
        "relationships_agent_validated": False,
        "relationships_agent_validation_conclusion_flag": False,
        "relationships_agent_validation_assessment_reasoning": "",
        "relationships_agent_validation_suggested_improvements": "",
        "relationships_current_validation_iteration": 0,
    }


def relationship_validation_reason_node(state: RelationshipGraphState):
    print("---ENTERING: REASON VALIDATION NODE---")

    if state.relationships_progress_tracker is not None:
        max_iterations = state.relationships_max_validation_iterations
        weight_by_retry = NODE_WEIGHTS["relationship_validation_reason_node"] / (
            state.relationships_max_retries + 1
        )
        progress = weight_by_retry * (
            (state.relationships_current_try - 1)
            + (state.relationships_current_validation_iteration / max_iterations)
        )
        state.relationships_progress_tracker.update(
            NODE_WEIGHTS["relationship_executor_reason_node"] + progress,
            "Validating relationships",
        )

    state.relationships_current_validation_iteration += 1
    if state.relationships_current_validation_iteration <= state.relationships_max_validation_iterations:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(VALIDATIONTOOLS, tool_choice="any")
    else:
        validation_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools([validate_simulated_relationships], tool_choice="any")

    full_prompt = format_relationship_validation_prompt(
        state.relationships_current_objective,
        state.relationships_executor_agent_relevant_logs,
        state.relationships_validation_messages,
    )
    response = validation_llm.invoke(full_prompt)
    return {
        "relationships_validation_messages": [response],
        "relationships_current_validation_iteration": state.relationships_current_validation_iteration,
    }

relationship_validation_tool_node = ToolNode(VALIDATIONTOOLS)
relationship_validation_tool_node.messages_key = "relationships_validation_messages"


def retry_executor_node(state: RelationshipGraphState):
    print("---ENTERING: RETRY NODE---")
    feedback = (
        "Here's some human feedback on how you have done so far on your task:\n "
        "You have still not completed your task\n Reason: "
        f"{state.relationships_agent_validation_assessment_reasoning}\n Suggestion/s:{state.relationships_agent_validation_suggested_improvements} "
    )
    feedback_message = HumanMessage(feedback)
    return {
        "relationships_executor_messages": [feedback_message],
        "messages_field_to_update": "relationships_executor_messages",
        "logs_field_to_update": "relationships_executor_applied_operations_log",
        "relationships_current_executor_iteration": 0,
        "relationships_current_try": state.relationships_current_try + 1,
    }


def final_node_success(state: RelationshipGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE SUCCESS---")
    SimulatedGameStateSingleton.commit()
    if state.relationships_progress_tracker is not None:
        state.relationships_progress_tracker.update(
            1.0, "Relationships task finalized successfully"
        )
    return {
        "relationships_task_succeeded_final": True,
    }


def final_node_failure(state: RelationshipGraphState):
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")
    SimulatedGameStateSingleton.rollback()
    if state.relationships_progress_tracker is not None:
        state.relationships_progress_tracker.update(
            1.0, "Relationships task finalized successfully"
        )
    return {
        "relationships_task_succeeded_final": False,
    }
