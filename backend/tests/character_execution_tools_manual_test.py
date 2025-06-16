# character_execution_tools_manual_test.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
)
from subsystems.agents.character_cast.schemas.simulated_characters import (
    SimulatedCharactersModel,
    CreateFullNPCArgs,
)
from subsystems.agents.character_cast.tools.character_tools import (
    create_full_npc,
    list_characters,
)


def print_step(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


if __name__ == "__main__":
    narrative_context = (
        "Evergreen village is abuzz with preparations for the yearly harvest festival. "
        "Tension grows as rumors of roaming bandits threaten the celebration."
    )

    characters_state = SimulatedCharactersModel()

    print_step("Create Characters")

    char1_args = CreateFullNPCArgs(
        identity=IdentityModel(full_name="Lia the Merchant", gender="female"),
        physical=PhysicalAttributesModel(
            appearance="Short woman with sharp eyes",
            clothing_style="travel garb",
            characteristic_items=["ledger"],
            distinctive_features=[],
        ),
        psychological=PsychologicalAttributesModel(
            personality_summary="Shrewd yet kind-hearted",
            backstory="Former street orphan turned successful trader",
        ),
        narrative=NarrativeWeightModel(
            narrative_role="ally",
            narrative_importance="secondary",
            narrative_purpose=[],
        ),
    )

    print(
        create_full_npc(
            **char1_args.model_dump(),
            simulated_characters_state=characters_state,
        )
    )

    char2_args = CreateFullNPCArgs(
        identity=IdentityModel(full_name="Bran the Guard", gender="male"),
        physical=PhysicalAttributesModel(
            appearance="Tall and muscular",
            clothing_style="town guard uniform",
            characteristic_items=["halberd"],
            distinctive_features=["scar across left cheek"],
        ),
        psychological=PsychologicalAttributesModel(
            personality_summary="Loyal and steadfast",
            backstory="Veteran of border skirmishes",
        ),
        narrative=NarrativeWeightModel(
            narrative_role="support",
            narrative_importance="secondary",
            narrative_purpose=[],
        ),
    )

    print(
        create_full_npc(
            **char2_args.model_dump(),
            simulated_characters_state=characters_state,
        )
    )

    print_step("Final State")
    print(list_characters(simulated_characters_state=characters_state))

    for cid, char in characters_state.simulated_characters.items():
        print(f"\nID: {cid}")
        print(char.model_dump_json(indent=2))

