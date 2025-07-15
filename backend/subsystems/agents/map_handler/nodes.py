from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI

from langgraph.prebuilt import ToolNode
from typing import Sequence, Dict, Any, List
from subsystems.agents.map_handler.schemas.graph_state import MapGraphState
from subsystems.agents.map_handler.tools.map_tools import EXECUTORTOOLS, VALIDATIONTOOLS, validate_simulated_map
from subsystems.agents.map_handler.prompts.reasoning import format_map_react_reason_prompt
from subsystems.agents.map_handler.prompts.validating import format_map_react_validation_prompt
from utils.message_window import get_valid_messages_window
from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage, AIMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

from simulated.singleton import SimulatedGameStateSingleton

from subsystems.agents.utils.logs import ToolLog, ClearLogs

NODE_WEIGHTS = {
    "map_executor_reason_node": 0.7,
    "map_validation_reason_node": 0.3,
}

def receive_objective_node(state: MapGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OBJECTIVE NODE---")
    SimulatedGameStateSingleton.begin_transaction() # Safety layer
    initial_summary=SimulatedGameStateSingleton.get_instance().read_only_map.get_summary_list()
    return {
        "map_current_try": 0,
        "messages_field_to_update": "map_executor_messages",
        "logs_field_to_update": "map_executor_applied_operations_log",
        "map_current_executor_iteration": 0,
        "map_initial_summary": initial_summary,
        "map_executor_messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        "map_task_finalized_by_agent": False,
        "map_task_finalized_justification": None,
        "map_current_validation_iteration": 0,
        "map_task_succeeded_final": False,
    }


executor_llm = ChatOpenAI(model="gpt-4.1-mini").bind_tools(EXECUTORTOOLS, tool_choice="any")

def map_executor_reason_node(state: MapGraphState):
    """
    Reasoning node. The llm requests the tool towards the next step
    """
    if state.map_progress_tracker is not None:
        # --- LÓGICA DE PROGRESO CORREGIDA ---
        max_retries = state.map_max_retries
        max_iterations = state.map_max_executor_iterations
        
        # 1. Base: ¿Cuánto progreso se completó en los reintentos ANTERIORES?
        # Usamos (try - 1) porque los reintentos son 1-based (empiezan en 1).
        progress_from_previous_tries = state.map_current_try / max_retries
        
        # 2. ¿Cuánto vale el bloque de progreso de ESTE reintento?
        weight_of_current_try_block = 1 / max_retries
        
        # 3. ¿Cuánto hemos avanzado DENTRO de la fase de ejecución de este intento? (un valor de 0.0 a 1.0)
        progress_within_execution_phase = state.map_current_executor_iteration / max_iterations
        
        # 4. El progreso total es la base + la fracción que llevamos de la fase de ejecución actual.
        total_local_progress = progress_from_previous_tries + (
            progress_within_execution_phase * weight_of_current_try_block * NODE_WEIGHTS["map_executor_reason_node"]
        )
        print("Total local progress:", total_local_progress)
        
        state.map_progress_tracker.update(total_local_progress, "Generating/Updating map")

    print("---ENTERING: REASON EXECUTION NODE---")

    full_prompt = format_map_react_reason_prompt(
        foundational_lore_document=state.map_foundational_lore_document,
        recent_operations_summary=state.map_recent_operations_summary,
        relevant_entity_details=state.map_relevant_entity_details,
        additional_information=state.map_additional_information,
        rules_and_constraints=state.map_rules_and_constraints,
        initial_summary=state.map_initial_summary,
        objective=state.map_current_objective,
        other_guidelines=state.map_other_guidelines,
        messages=get_valid_messages_window(state.map_executor_messages,30)
    )
    state.map_current_executor_iteration+=1

    print("CURRENT EXECUTOR ITERATION:", state.map_current_executor_iteration)
    
    response = executor_llm.invoke(full_prompt)

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
        "map_agent_validation_conclusion_flag": False,
        "map_agent_validation_assessment_reasoning": "",
        "map_agent_validation_suggested_improvements": "",
        "map_current_validation_iteration": 0
    }

def map_validation_reason_node(state: MapGraphState):
    """
    Reasoning validation node. The llm requests the tool querys and validates when has enought information or maxvalidation iteration is exceeded
    """
    print("---ENTERING: REASON VALIDATION NODE---")

    if state.map_progress_tracker is not None:
        # --- LÓGICA DE PROGRESO CORREGIDA ---
        max_retries = state.map_max_retries
        max_iterations = state.map_max_validation_iterations
        
        # 1. Base: ¿Cuánto progreso se completó en los reintentos ANTERIORES?
        # Usamos (try - 1) porque los reintentos son 1-based (empiezan en 1).
        progress_from_previous_tries = state.map_current_try / max_retries
        
        # 2. ¿Cuánto vale el bloque de progreso de ESTE reintento?
        weight_of_current_try_block = 1 / max_retries
        
        progress_within_execution_phase = weight_of_current_try_block * NODE_WEIGHTS["map_executor_reason_node"]
        # 3. ¿Cuánto hemos avanzado DENTRO de la fase de ejecución de este intento? (un valor de 0.0 a 1.0)
        progress_within_validation_phase = state.map_current_validation_iteration / max_iterations
        
        # 4. El progreso total es la base + la fracción que llevamos de la fase de ejecución actual.
        total_local_progress = progress_from_previous_tries + (
            progress_within_validation_phase * weight_of_current_try_block * NODE_WEIGHTS["map_executor_reason_node"]
        ) + progress_within_execution_phase

        print("Total local progress:", total_local_progress)
        
        state.map_progress_tracker.update(total_local_progress, "Generating/Updating map")

    if state.map_progress_tracker is not None:
        max_iterations = state.map_max_validation_iterations
        weight_of_map_val_by_retry = NODE_WEIGHTS["map_validation_reason_node"] / (state.map_max_retries+1)
        progress_of_map_val = weight_of_map_val_by_retry * (
           (state.map_current_try - 1) + (state.map_current_validation_iteration / max_iterations)
        )
        state.map_progress_tracker.update(NODE_WEIGHTS["map_executor_reason_node"] + progress_of_map_val, "Validating map")

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

def final_node_success(state: MapGraphState):
    """
    Last node of agent if succeeded on objective.
    """
    print("---ENTERING: LAST NODE OBJECTIVE SUCESS---")
    SimulatedGameStateSingleton.commit() # commit all changes done by agent

    if state.map_progress_tracker is not None:
        state.map_progress_tracker.update(1.0, "Map task finalized successfully")

    return {
        "map_task_succeeded_final": True,
    }

def final_node_failure(state: MapGraphState):
    """
    Last node of agent if failed on objective.
    """
    print("---ENTERING: LAST NODE OBJECTIVE FAILED---")

    SimulatedGameStateSingleton.rollback() # rollback all changes done by agent

    if state.map_progress_tracker is not None:
        state.map_progress_tracker.update(1.0, "Map task finalized successfully")

    return {
        "map_task_succeeded_final": False,
    }
