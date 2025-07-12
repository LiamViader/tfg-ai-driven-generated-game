from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.image_generation.scenarios.create.orchestrator import get_created_scenario_images_generation_app
from typing import Set, Optional
from subsystems.image_generation.scenarios.create.schemas import GraphState as ScenarioCreatedImagesGenerationState
import os
import base64
import asyncio
from dotenv import load_dotenv

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

    added_scenarios_ids = diff_result.scenarios.added

    if not added_scenarios_ids:
        print("  - No new scenarios detected. Skipping image generation.")
        return {"finalized_with_success": True}

    game_state = SimulatedGameStateSingleton.get_instance()

    scenarios_to_process = []
    for sid in added_scenarios_ids:
        scenario = game_state.read_only_map.find_scenario(sid)
        if scenario:
            scenarios_to_process.append(scenario.get_scenario_model())

    if not scenarios_to_process:
        print("  - No valid scenarios found for image generation.")
        return {"finalized_with_success": False}

    load_dotenv()
    scenarios_image_api_url = os.getenv("SCENARIOS_IMAGE_API_URL")
    if not scenarios_image_api_url:
        print("  - ERROR: SCENARIOS_IMAGE_API_URL environment variable not set.")
        return {"finalized_with_success": False}

    general_context = game_state.read_only_session.get_refined_prompt()
    if general_context is None:
        general_context = ""

    result = asyncio.run(created_scenario_images_generation_app.ainvoke(
        ScenarioCreatedImagesGenerationState(
            scenarios=scenarios_to_process,
            graphic_style=game_state.read_only_session.get_scenarios_graphic_style(),
            general_game_context=general_context,
            image_api_url=scenarios_image_api_url,
        )
    ))

    final_state = ScenarioCreatedImagesGenerationState(**result)

    if final_state.failed_scenarios:
        print(
            f"  - ERROR: Failed to generate {len(final_state.failed_scenarios)} scenario image(s)."
        )
        return {"finalized_with_success": False}

    output_dir = os.path.join("images", "scenarios")
    os.makedirs(output_dir, exist_ok=True)

    for scenario_state in final_state.successful_scenarios:
        if scenario_state.image_base64 is None:
            print(f"  - WARNING: Missing image data for {scenario_state.scenario.id}.")
            continue

        base_filename = scenario_state.scenario.id
        extension = ".png"
        
        image_path = os.path.join(output_dir, f"{base_filename}{extension}")
        counter = 1

        # 3. Bucle para encontrar un nombre de archivo único
        while os.path.exists(image_path):
            counter += 1
            # Crea un nuevo nombre con un sufijo, ej: "scenario_001_2.png"
            unique_filename = f"{base_filename}_{counter}{extension}"
            image_path = os.path.join(output_dir, unique_filename)
    
        try:
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(scenario_state.image_base64))
            print(f"  - Image saved to {image_path}")
        except Exception as e:
            print(f"  -  ERROR saving image to {image_path}: {e}")

    return {"finalized_with_success": True}


def finalize_generation_success(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION SUCCESS NODE---")
    SimulatedGameStateSingleton.commit()
    if state.initial_state_checkpoint_id:
        SimulatedGameStateSingleton.get_checkpoint_manager().delete_checkpoint(state.initial_state_checkpoint_id)
    return {
        "finalized_with_success": True
    }

def finalize_generation_error(state: GenerationGraphState):
    """Final node for the generation workflow."""
    print("---ENTERING: FINALIZE GENERATION ERROR NODE---")
    SimulatedGameStateSingleton.rollback()
    if state.initial_state_checkpoint_id:
        SimulatedGameStateSingleton.get_checkpoint_manager().delete_checkpoint(state.initial_state_checkpoint_id)
    return {
        "finalized_with_success": False
    }
