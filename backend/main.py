"""Manual test entrypoint for the complete generation graph."""

from subsystems.generation.orchestrator import get_generation_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState
from subsystems.generation.refinement_loop.pipelines import map_then_characters_pipeline


if __name__ == "__main__":
    pipeline = map_then_characters_pipeline()
    state = GenerationGraphState(
        initial_prompt=(
            "A world where wizards live in a secluded valley and harness elemental magic."
        ),
        refined_prompt_desired_word_length=300,
        refinement_pipeline_config=pipeline,
    )

    print("--- INVOKE GENERATION GRAPH ---")
    generation_app = get_generation_graph_app()
    final_state_data = generation_app.invoke(state, {"recursion_limit": 200})
    final_state = GenerationGraphState(**final_state_data)

    print("\n--- FINAL STATE ---\n")
    print("Main goal:", final_state.main_goal)
    print("Refined prompt:\n", final_state.refined_prompt)
    print("Refinement log:", final_state.refinement_pass_changelog)
