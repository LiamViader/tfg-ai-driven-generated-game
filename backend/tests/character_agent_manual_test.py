import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.agents.character_cast import get_character_graph_app
from subsystems.agents.character_cast.schemas.graph_state import CharacterGraphState


def print_step(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


if __name__ == "__main__":
    state = CharacterGraphState(
        global_narrative_context=(
            "a world where theres humanlike creatures (called Stoners) that are born with a stone incrustrated in their back. the stone keeps growing until they are crushed by its weight. some people that live freely and happy, their stone doesn't grow as fast. theres people that works mining other peoples stone with a pickaxe. when people dye, as the get crushed by its stone the only thing that remains in the surface is their stone, posing as a tombstone."
        ),
        character_rules_and_constraints=[
            "Characters should have unique personalities and physical atributes that make them outstand.",
        ],
        current_objective="Create two unique NPCs who could appear in this context. Then create the player character. Place them in the same scenario.",
        other_guidelines="Keep them distinct from canonical characters.",
        max_executor_iterations=3,
    )

    app = get_character_graph_app()

    print_step("Run Graph")
    final_data = app.invoke(state, {"recursion_limit": 40})
    final_state = CharacterGraphState(**final_data)

    print_step("Characters Created")
    for cid, char in final_state.working_simulated_characters.simulated_characters.items():
        print(f"ID: {cid}")
        print(char.model_dump_json(indent=2))

