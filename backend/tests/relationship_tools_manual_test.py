import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.agents.relationship.schemas.simulated_relationships import (
    SimulatedRelationshipsModel,
    GetRelationshipDetailsArgs,
    FinalizeSimulationArgs,
)
from subsystems.agents.relationship.tools.relationship_tools import (
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
    rel_types = {
        "friend": RelationshipType(name="friend"),
        "enemy": RelationshipType(name="enemy"),
    }
    sim_rels = SimulatedRelationshipsModel(relationship_types=rel_types)

    print_step("Create Relationship Type")
    print(create_relationship_type(
        name="mentor",
        explanation="Mentorship bond",
        simulated_relationships_state=sim_rels,
    ))

    print_step("Create Directed Relationship")
    print(create_directed_relationship(
        source_character_id="char_1",
        target_character_id="char_2",
        relationship_type="friend",
        intensity=7,
        simulated_relationships_state=sim_rels,
    ))

    print_step("Create Undirected Relationship")
    print(create_undirected_relationship(
        character_a_id="char_1",
        character_b_id="char_3",
        relationship_type="mentor",
        intensity=5,
        simulated_relationships_state=sim_rels,
    ))

    print_step("Create Directed Relationship")
    print(create_directed_relationship(
        source_character_id="char_2",
        target_character_id="char_1",
        relationship_type="enemy",
        intensity=6,
        simulated_relationships_state=sim_rels,
    ))

    print_step("Modify Intensity")
    print(modify_relationship_intensity(
        source_character_id="char_1",
        target_character_id="char_2",
        relationship_type="friend",
        new_intensity=9,
        simulated_relationships_state=sim_rels,
    ))

    print_step("Get Details")
    print(get_relationship_details(
        source_character_id="char_1",
        target_character_id="char_2",
        simulated_relationships_state=sim_rels,
    ))

    print_step("Finalize")
    result = finalize_simulation(
        justification="Relationships defined correctly.",
        simulated_relationships_state=sim_rels,
    )
    print(result)
