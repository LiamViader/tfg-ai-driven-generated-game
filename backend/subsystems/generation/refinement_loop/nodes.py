from subsystems.generation.refinement_loop.schemas.graph_state import RefinementLoopGraphState
from subsystems.generation.refinement_loop.utils.format_refinement_logs import format_window

def start_refinement_loop(state: RefinementLoopGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: START REFINEMENT LOOP NODE---")

    return {
        "refinement_current_pass": 0
    }

def prepare_next_step(state: RefinementLoopGraphState):
    """
    Node that prepares for the next step. This node is executed after every step
    """
    #AQUI S'HAURIA DE FER EL RESUM DE LES OPERACIONS MES VELLES EN CAS QUE CALGUI
    return {
        "refinement_current_pass": state.refinement_current_pass+1
    }

def map_step_start(state: RefinementLoopGraphState):
    """
    Sets up the state for the pass to refine the map
    """
    map_foundational_info = state.refined_prompt
    applied_operations_log = "Old operations summary: " + state.changelog_old_operations_summary + "Most recent operations:" + format_window(6,state.refinement_pass_changelog)
    relevant_entities_str = ""
    additional_info_str = ""
    current_step=state.refinement_pipeline_config.steps[state.refinement_current_pass]
    return {
        "map_foundational_lore_document": map_foundational_info,
        "map_recent_operations_summary": applied_operations_log,
        "map_relevant_entity_details": relevant_entities_str,
        "map_additional_information": additional_info_str,
        "map_rules_and_constraints": current_step.rules_and_constraints,
        "map_other_guidelines": current_step.other_guidelines,
        "map_current_objective": current_step.objective_prompt,
        "map_max_executor_iterations": current_step.max_executor_iterations,
        "map_max_validation_iterations": current_step.max_validation_iterations,
        "map_max_retries": current_step.max_retries
    }

def map_step_finish(state: RefinementLoopGraphState):
    """
    Postprocesses the finished map step.
    """
    return {
        "operations_log_to_summarize": state.map_executor_applied_operations_log,
        "last_step_succeeded": state.map_task_succeeded_final
    }

def finalize_step(state: RefinementLoopGraphState):
    """
    Aux node after any component finished
    """
    return {
        
    }
