
from subsystems.generation.orchestrator import get_generation_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.refinement_loop.pipelines import (
    alternating_expansion_pipeline,
    map_then_characters_pipeline,
    characters_only_pipeline,
    map_characters_relationships_pipeline,
    map_characters_relationships_narrative_pipeline,
    map_only_pipeline
)
from utils.visualize_graph import visualize_map_graph
from core_game.game_state.singleton import GameStateSingleton
from utils.progress_tracker import ProgressTracker


USER_PROMPT = """
About cars that are alive.
"""

def print_progress(global_progress: float, message: str):
    percent = round(global_progress * 100, 2)
    print(f"[PROGRESS] {percent}% - {message}")

if __name__ == "__main__":
    pipeline = map_then_characters_pipeline()
    tracker = ProgressTracker(weight=1.0, update_fn=print_progress)
    state = GenerationGraphState(
        initial_prompt=USER_PROMPT,
        refined_prompt_desired_word_length=200,
        refinement_pipeline_config=pipeline,
    )

    state.generation_progress_tracker = tracker 

    print("--- INVOKE GENERATION GRAPH ---")
    generation_app = get_generation_graph_app()
    final_state_data = generation_app.invoke(state, {"recursion_limit": 500})
    final_state = GenerationGraphState(**final_state_data)

    print("\n--- FINAL STATE ---\n")
    print("Main goal:", final_state.main_goal)
    print("Refined prompt:\n", final_state.refined_prompt)
    print("Refinement log:", final_state.refinement_pass_changelog)

    visualize_map_graph(GameStateSingleton.get_instance())
