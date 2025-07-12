from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.refinement_loop.utils.format_refinement_logs import format_window
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.utils.logs import ToolLog, ClearLogs
def start_refinement_loop(state: RefinementLoopGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: START REFINEMENT LOOP NODE---")

    return {
        "refinement_current_pass": 0,
    }

def prepare_next_step(state: RefinementLoopGraphState):
    """
    Node that prepares for the next step. This node is executed after every step
    """
    print("---ENTERING: PREPARE NEXT STEP---")
    
    if state.refinement_current_pass+1 < len(state.refinement_pipeline_config.steps):
        agentName = state.refinement_pipeline_config.steps[state.refinement_current_pass+1].agent_name
    else:
        agentName = state.current_agent_name
    
    return {
        "refinement_current_pass": state.refinement_current_pass+1,
        "current_agent_name": agentName,
    }

def add_agent_log_to_changelog(state: RefinementLoopGraphState):
    """
    Adds the summarized log to the changelog
    """
    #AQUI S'HAURIA DE FER EL RESUM DE LES OPERACIONS MES VELLES EN CAS QUE CALGUI

    return {
        "refinement_pass_changelog": [state.sumarized_operations_result]
    }

def map_step_start(state: RefinementLoopGraphState):
    """
    Sets up the state for the pass to refine the map
    """

    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6,state.refinement_pass_changelog)
    relevant_entities_str = "" # AQUI S'HAURIA DE INJECTAR INFORMACIO D'ENTITATS QUE PUGUIN SER UTILS, FENT RAG A PARTIR DE LES ULTIMES OPERACIONS I TENINT EN COMPTE QUE LI POT INTERESSAR A AQUEST AGENT I DE QUI ERA CADA OPERACIO
    additional_info_str = ""
    current_step=state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "map_foundational_lore_document": state.refinement_foundational_world_info,
        "map_recent_operations_summary": applied_operations_log,
        "map_relevant_entity_details": relevant_entities_str,
        "map_additional_information": additional_info_str,
        "map_rules_and_constraints": current_step.rules_and_constraints,
        "map_other_guidelines": current_step.other_guidelines,
        "map_current_objective": current_step.objective_prompt,
        "map_max_executor_iterations": current_step.max_executor_iterations,
        "map_max_validation_iterations": current_step.max_validation_iterations,
        "map_max_retries": current_step.max_retries,
        "map_executor_applied_operations_log": ClearLogs(),
        "map_validator_applied_operations_log": ClearLogs()
    }

def map_step_finish(state: RefinementLoopGraphState):
    """
    Postprocesses the finished map step.
    """
    return {
        "operations_log_to_summarize": state.map_executor_applied_operations_log,
        "last_step_succeeded": state.map_task_succeeded_final,
    }

def characters_step_start(state: RefinementLoopGraphState):
    """
    Sets up the state for the pass to refine the map
    """
    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6,state.refinement_pass_changelog)
    relevant_entities_str = ""
    additional_info_str = ""
    current_step=state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "characters_foundational_lore_document": state.refinement_foundational_world_info,
        "characters_recent_operations_summary": applied_operations_log,
        "characters_relevant_entity_details": relevant_entities_str,
        "characters_additional_information": additional_info_str,
        "characters_rules_and_constraints": current_step.rules_and_constraints,
        "characters_other_guidelines": current_step.other_guidelines,
        "characters_current_objective": current_step.objective_prompt,
        "characters_max_executor_iterations": current_step.max_executor_iterations,
        "characters_max_validation_iterations": current_step.max_validation_iterations,
        "characters_max_retries": current_step.max_retries,
        "characters_executor_applied_operations_log": ClearLogs(),
        "characters_validator_applied_operations_log": ClearLogs()
    }

def characters_step_finish(state: RefinementLoopGraphState):
    """
    Postprocesses the finished map step.
    """
    return {
        "operations_log_to_summarize": state.characters_executor_applied_operations_log,
        "last_step_succeeded": state.characters_task_succeeded_final
    }

def relationship_step_start(state: RefinementLoopGraphState):
    """Sets up the state for the pass to refine the relationships"""

    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6, state.refinement_pass_changelog)
    relevant_entities_str = ""
    additional_info_str = ""
    current_step = state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "relationships_foundational_lore_document": state.refinement_foundational_world_info,
        "relationships_recent_operations_summary": applied_operations_log,
        "relationships_relevant_entity_details": relevant_entities_str,
        "relationships_additional_information": additional_info_str,
        "relationships_rules_and_constraints": current_step.rules_and_constraints,
        "relationships_other_guidelines": current_step.other_guidelines,
        "relationships_current_objective": current_step.objective_prompt,
        "relationships_max_executor_iterations": current_step.max_executor_iterations,
        "relationships_max_validation_iterations": current_step.max_validation_iterations,
        "relationships_max_retries": current_step.max_retries,
        "relationships_executor_applied_operations_log": ClearLogs(),
        "relationships_validator_applied_operations_log": ClearLogs(),
    }

def relationship_step_finish(state: RefinementLoopGraphState):
    """Postprocesses the finished relationship step."""
    return {
        "operations_log_to_summarize": state.relationships_executor_applied_operations_log,
        "last_step_succeeded": state.relationships_task_succeeded_final,
    }

def narrative_step_start(state: RefinementLoopGraphState):
    """Sets up the state for the pass to refine the narrative"""

    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6, state.refinement_pass_changelog)
    relevant_entities_str = ""
    additional_info_str = ""
    current_step = state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "narrative_foundational_lore_document": state.refinement_foundational_world_info,
        "narrative_recent_operations_summary": applied_operations_log,
        "narrative_relevant_entity_details": relevant_entities_str,
        "narrative_additional_information": additional_info_str,
        "narrative_rules_and_constraints": current_step.rules_and_constraints,
        "narrative_other_guidelines": current_step.other_guidelines,
        "narrative_current_objective": current_step.objective_prompt,
        "narrative_max_executor_iterations": current_step.max_executor_iterations,
        "narrative_max_validation_iterations": current_step.max_validation_iterations,
        "narrative_max_retries": current_step.max_retries,
        "narrative_executor_applied_operations_log": ClearLogs(),
        "narrative_validator_applied_operations_log": ClearLogs(),
    }

def narrative_step_finish(state: RefinementLoopGraphState):
    """Postprocesses the finished narrative step."""
    return {
        "operations_log_to_summarize": state.narrative_executor_applied_operations_log,
        "last_step_succeeded": state.narrative_task_succeeded_final,
    }

def events_step_start(state: RefinementLoopGraphState):
    """Sets up the state for the pass to refine the game events"""

    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6, state.refinement_pass_changelog)
    relevant_entities_str = ""
    additional_info_str = ""
    current_step = state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "events_foundational_lore_document": state.refinement_foundational_world_info,
        "events_recent_operations_summary": applied_operations_log,
        "events_relevant_entity_details": relevant_entities_str,
        "events_additional_information": additional_info_str,
        "events_rules_and_constraints": current_step.rules_and_constraints,
        "events_other_guidelines": current_step.other_guidelines,
        "events_current_objective": current_step.objective_prompt,
        "events_max_executor_iterations": current_step.max_executor_iterations,
        "events_max_validation_iterations": current_step.max_validation_iterations,
        "events_max_retries": current_step.max_retries,
        "events_executor_applied_operations_log": ClearLogs(),
        "events_validator_applied_operations_log": ClearLogs(),
    }

def events_step_finish(state: RefinementLoopGraphState):
    """Postprocesses the finished events step."""
    return {
        "operations_log_to_summarize": state.events_executor_applied_operations_log,
        "last_step_succeeded": state.events_task_succeeded_final,
    }


def finalize_step(state: RefinementLoopGraphState):
    """
    Aux node after any component finished
    """
    return {
        
    }

def finalize_refinement_loop(state: RefinementLoopGraphState):
    """
    Node called when the refinement_loop has finished
    """
    #TODO CHECK HOW MANY PASSES WERE SUCCESSFULL AND DECIDE WHETHER TO FINALIZE WITH SUCCESS OR WITH FAILURE
    return {
        "finalized_with_success": True
    }
