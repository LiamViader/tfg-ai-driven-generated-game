"""Manual test entrypoint for the complete generation graph."""

from subsystems.generation.orchestrator import get_generation_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.refinement_loop.pipelines import alternating_expansion_pipeline
from utils.visualize_graph import visualize_map_graph
from core_game.game_state.singleton import GameStateSingleton

USER_PROMPT = """
a world where theres humanlike creatures (called Stoners) that are born with a stone incrustrated in their back. the stone keeps growing until they are crushed by its weight. some people that live freely and happy, their stone doesn't grow as fast. theres people that works mining other peoples stone with a pickaxe. when people dye, as the get crushed by its stone the only thing that remains in the surface is their stone, posing as a tombstone
"""

if __name__ == "__main__":
    pipeline = alternating_expansion_pipeline()
    state = GenerationGraphState(
        initial_prompt=USER_PROMPT,
        refined_prompt_desired_word_length=200,
        refinement_pipeline_config=pipeline,
    )

    print("--- INVOKE GENERATION GRAPH ---")
    generation_app = get_generation_graph_app()
    final_state_data = generation_app.invoke(state, {"recursion_limit": 500})
    final_state = GenerationGraphState(**final_state_data)

    print("\n--- FINAL STATE ---\n")
    print("Main goal:", final_state.main_goal)
    print("Refined prompt:\n", final_state.refined_prompt)
    print("Refinement log:", final_state.refinement_pass_changelog)

    # Visualize the final map state
    visualize_map_graph(GameStateSingleton.get_instance())
