"""Manual test for the character agent.

This script initializes the character management agent with a
Lord of the Rings narrative context and requests the creation of
two characters. The resulting characters are printed in JSON format.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.agents.character import get_character_graph_app
from subsystems.agents.character.schemas.graph_state import CharacterGraphState


def print_step(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


if __name__ == "__main__":
    state = CharacterGraphState(
        global_narrative_context=(
            "The armies of Middle-earth prepare for the final battle against Sauron."
        ),
        character_rules_and_constraints=[
            "Characters must fit within Tolkien's world.",
            "They should not contradict established lore.",
        ],
        current_objective="Create two unique NPCs who could appear in this context.",
        other_guidelines="Keep them distinct from canonical characters."
    )

    app = get_character_graph_app()

    print_step("Run Graph")
    final_data = app.invoke(state, {"recursion_limit": 40})
    final_state = CharacterGraphState(**final_data)

    print_step("Characters Created")
    for cid, char in final_state.working_simulated_characters.simulated_characters.items():
        print(f"ID: {cid}")
        print(char.model_dump_json(indent=2))

