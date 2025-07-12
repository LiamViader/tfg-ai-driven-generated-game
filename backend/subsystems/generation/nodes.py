from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.image_generation.scenarios.create.orchestrator import get_created_scenario_images_generation_app
from typing import Set, Optional


def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    SimulatedGameStateSingleton.begin_transaction()

    manager = SimulatedGameStateSingleton.get_checkpoint_manager()
    checkpoint_id = manager.create_checkpoint()
    
    return {"initial_state_checkpoint_id": checkpoint_id}

def prepare_refinement(state: GenerationGraphState):
    """Intermidiate node between seed generation and refinement, prepares refinement"""
    print("---ENTERING: PREPARE REFINEMENT NODE---")

    game_state = SimulatedGameStateSingleton.get_instance()
    refined_prompt = game_state.read_only_session.get_refined_prompt()
    assert refined_prompt is not None, "Refined prompt should not be None at prepare refinement"  

    main_goal = game_state.read_only_narrative.get_main_goal()
    assert main_goal is not None, "Player main goal should not be None at prepare refinement"

    foundational_info = refined_prompt + "\n In this narrative world, the player has the following goal/objective: " + main_goal

    return{
        "refinement_foundational_world_info": foundational_info
    }

def ensure_map_connectivity(state: GenerationGraphState):
    """
    Ensures the entire game map is a single, connected graph by applying a
    strategy based on the size of the main connected component.

    This node acts as a post-processing step after the initial map generation.
    It analyzes the map's connection graph
    and decides on a course of action:

    - If > 75% of scenarios are in the main cluster, it prunes the rest.
    - If > 50%, it connects smaller islands to the main cluster until the 75%
      threshold is met, then prunes any remaining islands.
    - If <= 50%, it raises an error, halting the generation process.
    """
    print("---ENTERING: ENSURE MAP CONNECTIVITY NODE---")
    game_state = SimulatedGameStateSingleton.get_instance()

    # --- Helper Functions ---
    def _handle_pruning() -> dict:
        """Calls the pruning method and returns the appropriate final state."""
        print("  - Pruning remaining isolated islands...")
        if not game_state.prune_scenarios_outside_main_cluster():
            print("  - WARNING: Something went wrong while pruning.")
            return {"finalized_with_success": False}
        else:
            print("  - Pruning successful.")
            return {"finalized_with_success": True}

    def _get_connectivity_state() -> tuple[int, Optional[Set[str]], float]:
        """Fetches and computes the current connectivity state of the map."""
        total = game_state.read_only_map.get_scenario_count()
        main_cluster = game_state.read_only_map.get_main_cluster()
        if not total or not main_cluster:
            return 0, None, 0.0
        ratio = len(main_cluster) / total
        return total, main_cluster, ratio

    # --- Main Logic ---
    total_scenarios, _, connectivity_ratio = _get_connectivity_state()
    all_clusters = game_state.read_only_map.get_all_clusters()
    if not total_scenarios:
        print("  - Map is empty. Finalizing by error.")
        return {"finalized_with_success": False}
    elif len(all_clusters) == 1:
        print("  - Map is already connected. No action needed.")
        return {"finalized_with_success": True}

    print(f"  - Initial connectivity ratio: {connectivity_ratio:.2%}")

    # Case 1: High connectivity (> 75%)
    if connectivity_ratio > 0.75:
        print("  - STRATEGY: Pruning isolated islands.")
        return _handle_pruning()

    # Case 2: Medium connectivity (> 50%)
    elif connectivity_ratio > 0.5:
        print("  - STRATEGY: Connecting islands to meet the 75% threshold.")
        
        current_ratio = connectivity_ratio
        while current_ratio < 0.75:
            print(f"\n  - Ratio at {current_ratio:.2%} is below 0.75. Attempting to connect largest island...")
            success = game_state.map.connect_largest_island_to_main_cluster()
            if not success:
                print("  - ❌ FAILED to connect largest island. Halting process.")
                return {"finalized_with_success": False}
            
            _, _, current_ratio = _get_connectivity_state()
            print(f"  - New connectivity ratio: {current_ratio:.2%}")

        return _handle_pruning()

    # Case 3: Low connectivity (<= 50%)
    else:
        error_message = (
            f"Map connectivity is too low ({connectivity_ratio:.2%}). "
            f"Generation cannot proceed reliably. Halting with an error."
        )
        print(f"  - ❌ ERROR: {error_message}")
        return {"finalized_with_success": False}


def generate_images(state: GenerationGraphState):
    """Node for generating all images for the added or (TO DO)[modified] entities"""
    print("---ENTERING: PARALLEL IMAGE GENERATION NODE---")

    created_scenario_images_generation_app = get_created_scenario_images_generation_app()

    checkpoint_id = state.initial_state_checkpoint_id
    if not checkpoint_id:
        print("  -  ERROR: No initial state checkpoint ID found. Cannot calculate diff.")
        return {"finalized_with_success": False}

    manager = SimulatedGameStateSingleton.get_checkpoint_manager()
    diff_result = manager.diff(from_checkpoint=checkpoint_id)

    added_scenarios_ids = diff_result["scenarios"]["added"]

    return {}


def finalize_generation_success(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    SimulatedGameStateSingleton.commit()
    return {
        "finalized_with_success": True
    }

def finalize_generation_error(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION NODE---")
    SimulatedGameStateSingleton.rollback()
    return {
        "finalized_with_success": False
    }
