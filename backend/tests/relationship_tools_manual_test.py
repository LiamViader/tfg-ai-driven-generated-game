import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.agents.relationship.schemas.simulated_relationships import (
    SimulatedRelationshipsModel,
    SetRelationshipArgs,
    GetRelationshipDetailsArgs,
    FinalizeSimulationArgs,
)
from subsystems.agents.relationship.tools.relationship_tools import (
    set_relationship,
    get_relationship_details,
    finalize_simulation,
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

    print_step("Set Relationship")
    print(set_relationship(
        source_character_id="char_1",
        target_character_id="char_2",
        relationship_type="friend",
        intensity=7,
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
