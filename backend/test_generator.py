from subsystems.generation.orchestrator import get_generator_graph_app
from subsystems.generation.schemas.graph_state import GenerationGraphState


if __name__ == '__main__':
    state = GenerationGraphState(
        initial_prompt="a world where theres humanlike creatures that are born with a stone incrustrated in their back. the stone keeps growing until they are crushed by its weight. some people that live freely and happy, their stone doesn't grow as fast. theres people that works mining other peoples stone with a pickaxe. when people dye, as the get crushed by its stone the only thing that remains in the surface is their stone, posing as a tombstone",
        generate_main_goal_max_attempts=2,
    )
    print("--- INVOKE ---")
    generation_app=get_generator_graph_app()
    final_state = generation_app.invoke(state,{"recursion_limit": 200})
    final_graph_state_instance = GenerationGraphState(**final_state)

    print("\n--- FINAL STATE ---\n\n")
    print(final_graph_state_instance.main_goal)
