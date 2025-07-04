import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.relationship_handler.tools.relationship_tools import (
    get_relationship_details,
    finalize_simulation,
    create_relationship_type,
    create_undirected_relationship,
    create_directed_relationship,
    modify_relationship_intensity,
)
from core_game.character.schemas import RelationshipType


def print_step(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


if __name__ == "__main__":
    SimulatedGameStateSingleton.reset_instance()
    state = SimulatedGameStateSingleton.get_instance()
    state.relationships.create_relationship_type(name="friend")
    state.relationships.create_relationship_type(name="enemy")

    print_step("Create Relationship Type")
    print(create_relationship_type(
        name="mentor",
        explanation="Mentorship bond",
    ))

    print_step("Create Directed Relationship")
    print(create_directed_relationship(
        source_character_id="char_1",
        target_character_id="char_2",
        relationship_type="friend",
        intensity=7,
    ))

    print_step("Create Undirected Relationship")
    print(create_undirected_relationship(
        character_a_id="char_1",
        character_b_id="char_3",
        relationship_type="mentor",
        intensity=5,
    ))

    print_step("Create Directed Relationship")
    print(create_directed_relationship(
        source_character_id="char_2",
        target_character_id="char_1",
        relationship_type="enemy",
        intensity=6,
    ))

    print_step("Modify Intensity")
    print(modify_relationship_intensity(
        source_character_id="char_1",
        target_character_id="char_2",
        relationship_type="friend",
        new_intensity=9,
    ))

    print_step("Get Details")
    print(get_relationship_details(
        source_character_id="char_1",
        target_character_id="char_2",
    ))

    print_step("Finalize")
    result = finalize_simulation(
        justification="Relationships defined correctly.",
    )
    print(result)
