from subsystems.generation.schemas.graph_state import GenerationGraphState
from simulated.singleton import SimulatedGameStateSingleton
from subsystems.image_generation.scenarios.create.orchestrator import get_created_scenario_images_generation_app
from subsystems.image_generation.scenarios.create.schemas import GraphState as ScenarioCreatedImagesGenerationState
from subsystems.image_generation.characters.create.schemas import GraphState as CharacterCreatedImagesGenerationState
from subsystems.image_generation.characters.create.orchestrator import get_created_character_images_generation_app
from core_game.character.schemas import CharacterBaseModel
from core_game.map.schemas import ScenarioModel, ScenarioImageGenerationTemplate
from typing import Set, Optional, Tuple, List, Dict, Any
from simulated.versioning.deltas.checkpoints.internal import InternalStateCheckpoint


import os
import base64
import asyncio
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

def start_generation(state: GenerationGraphState):
    """Initial node for the generation workflow."""
    print("---ENTERING: START GENERATION NODE---")
    SimulatedGameStateSingleton.begin_transaction()

    manager = SimulatedGameStateSingleton.get_checkpoint_manager()
    checkpoint_id = manager.create_checkpoint(
        checkpoint_type=InternalStateCheckpoint,
        checkpoint_id="initial_generation_state" # Es buena práctica darle un ID legible
    )
    
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


def _get_entities_for_generation(checkpoint_id: str) -> Tuple[List[ScenarioModel], List[CharacterBaseModel]]:
    """
    Calculates the diff from the checkpoint and returns lists of scenarios
    and characters that require image generation.
    """
    print("  - Calculating diff from checkpoint to find new/modified entities...")
    manager = SimulatedGameStateSingleton.get_checkpoint_manager()
    diff_result = manager.generate_internal_diff(from_id=checkpoint_id)
    game_state = SimulatedGameStateSingleton.get_instance()

    # Process scenarios
    added_scenario_ids = diff_result.scenarios.added
    scenarios_to_process = [
        s.get_scenario_model() for sid in added_scenario_ids 
        if (s := game_state.read_only_map.find_scenario(sid)) is not None
    ]

    added_character_ids = diff_result.characters.added
    characters_to_process = [
        c.get_model() for cid in added_character_ids
        if (c := game_state.read_only_characters.get_character(cid)) is not None
    ]

    print(f"  - Found {len(scenarios_to_process)} scenarios and {len(characters_to_process)} characters to process.")
    return scenarios_to_process, characters_to_process

def _run_image_generation_subgraphs(
    scenarios: List[ScenarioModel], 
    characters: List[CharacterBaseModel], 
    scenarios_image_api_url: str
) -> Dict[str, Any]:
    """
    Prepares and runs the image generation subgraphs for scenarios and characters in parallel.
    """
    game_state = SimulatedGameStateSingleton.get_instance()
    general_context = game_state.read_only_session.get_refined_prompt() or ""
    
    tasks = []
    
    if scenarios:
        print("  - Preparing scenario image generation task...")
        scenario_app = get_created_scenario_images_generation_app()
        scenario_input = ScenarioCreatedImagesGenerationState(
            scenarios=scenarios,
            graphic_style=game_state.read_only_session.get_scenarios_graphic_style(),
            general_game_context=general_context,
            image_api_url=scenarios_image_api_url,
        )
        tasks.append(scenario_app.ainvoke(scenario_input))

    # Prepare character generation task if needed
    if characters:
        print("  - Preparing character image generation task...")
        character_app = get_created_character_images_generation_app()
        character_input = CharacterCreatedImagesGenerationState(
            characters=characters,
            graphic_style=game_state.read_only_session.get_characters_graphic_style(),
            general_game_context=general_context,
            use_image_ref=True
        )
        tasks.append(character_app.ainvoke(character_input))

    if not tasks:
        return {}

    async def run_parallel_tasks():
        """Helper coroutine to run tasks with asyncio.gather."""
        return await asyncio.gather(*tasks)

    print(f"  - Running {len(tasks)} generation subgraphs in parallel...")
    all_results = asyncio.run(run_parallel_tasks())
    
    # Map results back based on the order tasks were added
    final_results = {}
    result_index = 0
    if scenarios:
        final_results["scenario_results"] = all_results[result_index]
        result_index += 1
    if characters:
        final_results["character_results"] = all_results[result_index]

    return final_results

def _save_images(result_data: Dict[str, Any]) -> bool:
    """Saves the generated images from both scenarios and characters to disk."""
    all_successful = True

    if "scenario_results" in result_data:
        scenario_final_state = ScenarioCreatedImagesGenerationState(**result_data["scenario_results"])
        if scenario_final_state.failed_scenarios:
            print(f"  - ERROR: Failed to generate {len(scenario_final_state.failed_scenarios)} scenario image(s).")
            all_successful = False

        output_dir = os.path.join("images", "scenarios")
        os.makedirs(output_dir, exist_ok=True)
        print(f"  - Saving {len(scenario_final_state.successful_scenarios)} scenario images to '{output_dir}'...")

        for scenario_state in scenario_final_state.successful_scenarios:
            if scenario_state.image_base64 is None:
                print(f"  - WARNING: Missing image data for {scenario_state.scenario.id}.")
                continue

            base_filename = scenario_state.scenario.id
            extension = ".png"
            
            image_path = os.path.join(output_dir, f"{base_filename}{extension}")
            counter = 1

            # Loop to find unique name
            while os.path.exists(image_path):
                counter += 1
                # Creates new name with suffix, eg: "scenario_001_2.png"
                unique_filename = f"{base_filename}_{counter}{extension}"
                image_path = os.path.join(output_dir, unique_filename)
        
            try:
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(scenario_state.image_base64))
                print(f"  - Image saved to {image_path}")
                assert scenario_state.generation_payload is not None
                SimulatedGameStateSingleton.get_instance().map.attach_new_image(scenario_state.scenario.id, image_path, scenario_state.generation_payload)
            except Exception as e:
                print(f"  -  ERROR saving image to {image_path}: {e}")

    if "character_results" in result_data:
        char_final_state = CharacterCreatedImagesGenerationState(**result_data["character_results"])
        if char_final_state.failed_characters:
            print(f"  - ERROR: Failed to generate {len(char_final_state.failed_characters)} character image(s).")
            all_successful = False
        
        output_dir = os.path.join("images", "characters")
        os.makedirs(output_dir, exist_ok=True)
        print(f"  - Saving {len(char_final_state.successful_characters)} character images to '{output_dir}'...")

        for character_state in char_final_state.successful_characters:
            if character_state.image_base64 is None:
                print(f"  - WARNING: Missing image data for {character_state.character.id}.")
                continue

            base_filename = character_state.character.id
            extension = ".png"
            
            image_path = os.path.join(output_dir, f"{base_filename}{extension}")
            counter = 1

            # Loop to find unique name
            while os.path.exists(image_path):
                counter += 1
                # Creates new name with suffix, eg: "character_001_2.png"
                unique_filename = f"{base_filename}_{counter}{extension}"
                image_path = os.path.join(output_dir, unique_filename)
        
            try:
                with open(image_path, "wb") as f:
                    f.write(base64.b64decode(character_state.image_base64))
                print(f"  - Image saved to {image_path}")
                assert character_state.generated_image_prompt is not None
                SimulatedGameStateSingleton.get_instance().characters.attach_new_image(character_state.character.id, image_path, character_state.generated_image_prompt)
            except Exception as e:
                print(f"  -  ERROR saving image to {image_path}: {e}")

    return all_successful

def generate_images(state: GenerationGraphState):
    """Node for generating all images for the added entities"""
    print("---ENTERING: PARALLEL IMAGE GENERATION NODE---")
    
    load_dotenv()
    checkpoint_id = state.initial_state_checkpoint_id
    if not checkpoint_id:
        print("  - ERROR: No initial state checkpoint ID found.")
        return {"finalized_with_success": False}
    
    scenarios_image_api_url = os.getenv("SCENARIOS_IMAGE_API_URL")

    if not scenarios_image_api_url:
        print("  - ERROR: SCENARIOS_IMAGE_API_URL environment variable not set.")
        return {"finalized_with_success": False}

    scenarios_to_process, characters_to_process = _get_entities_for_generation(checkpoint_id)

    if not scenarios_to_process and not characters_to_process:
        print("  - No new or visually modified entities found. Skipping image generation.")
        return {"finalized_with_success": True}

    results = _run_image_generation_subgraphs(scenarios_to_process,characters_to_process,scenarios_image_api_url)
    success = _save_images(results)
    
    return {"finalized_with_success": success}



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
