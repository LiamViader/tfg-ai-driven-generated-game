# character_execution_tools_manual_test.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    NarrativePurposeModel,
)
from subsystems.agents.character_handler.schemas.simulated_characters import (
    SimulatedCharactersModel,
    CreateNPCArgs,
    CreatePlayerArgs,
)
from subsystems.agents.character_handler.tools.character_tools import (
    create_npc,
    get_character_details,
    create_player,
    place_character,
    remove_character_from_scenario,
    delete_character,
    list_characters,
    get_player_details,
    modify_identity,
    modify_knowledge,
    modify_dynamic_state,
    modify_narrative,
    list_characters_by_scenario
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

    char1_args = CreateNPCArgs(
        identity=IdentityModel(
            full_name="Lia the Merchant",
            gender="female",
            age=30,
            profession="merchant",
            species="human",
            alignment="neutral",
        ),
        physical=PhysicalAttributesModel(
            appearance="Short woman with sharp eyes",
            visual_prompt="Short woman with sharp eyes wearing travel garb and carrying a ledger.",
            clothing_style="travel garb",
            characteristic_items=["ledger"],
            distinctive_features=[],
        ),
        psychological=PsychologicalAttributesModel(
            personality_summary="Shrewd yet kind-hearted",
            personality_tags=["shrewd", "kind"],
            motivations=["profit"],
            values=["fairness"],
            fears_and_weaknesses=[],
            communication_style="direct",
            backstory="Former street orphan turned successful trader",
            quirks=["hums while working"],
        ),
        narrative=NarrativeWeightModel(
            narrative_role="ally",
            current_narrative_importance="secondary",
            narrative_purposes=[
                NarrativePurposeModel(mission="support protagonist", is_hidden=False)
            ],
        ),
    )

    print(
        create_npc.invoke(
            {
                **char1_args.model_dump(),
                "simulated_characters_state": characters_state,
            }
        )
    )

    char2_args = CreateNPCArgs(
        identity=IdentityModel(
            full_name="Bran the Guard",
            gender="male",
            age=35,
            profession="guard",
            species="human",
            alignment="lawful good",
        ),
        physical=PhysicalAttributesModel(
            appearance="Tall and muscular",
            visual_prompt="Tall and muscular guard in uniform wielding a halberd, scar across left cheek.",
            clothing_style="town guard uniform",
            characteristic_items=["halberd"],
            distinctive_features=["scar across left cheek"],
        ),
        psychological=PsychologicalAttributesModel(
            personality_summary="Loyal and steadfast",
            personality_tags=["loyal"],
            motivations=["duty"],
            values=["honor"],
            fears_and_weaknesses=[],
            communication_style="formal",
            backstory="Veteran of border skirmishes",
            quirks=["polishes armor obsessively"],
        ),
        narrative=NarrativeWeightModel(
            narrative_role="ally",
            current_narrative_importance="secondary",
            narrative_purposes=[
                NarrativePurposeModel(mission="defend town", is_hidden=False), NarrativePurposeModel(mission="investigate bandits", is_hidden=True)
            ],
        ),
    )

    print(
        create_npc.invoke(
            {
                **char2_args.model_dump(),
                "simulated_characters_state": characters_state,
            }
        )
    )

    print_step("Create Player")

    player_args = CreatePlayerArgs(
        identity=IdentityModel(
            full_name="Arin the Wanderer",
            gender="non-binary",
            age=24,
            profession="adventurer",
            species="human",
            alignment="chaotic good",
        ),
        physical=PhysicalAttributesModel(
            appearance="Lean and quick on their feet",
            visual_prompt="Lean and quick wanderer in travel gear carrying a map and lute, tattooed arms visible.",
            clothing_style="traveler's gear",
            characteristic_items=["map", "lute"],
            distinctive_features=["tattooed arms"],
        ),
        psychological=PsychologicalAttributesModel(
            personality_summary="Curious and brave",
            personality_tags=["curious", "brave"],
            motivations=["explore"],
            values=["freedom"],
            fears_and_weaknesses=[],
            communication_style="friendly",
            backstory="Left home seeking adventure",
            quirks=["talks to animals"],
        ),
        present_in_scenario="scenario_001",
    )

    print(
        create_player.invoke(
            {
                **player_args.model_dump(),
                "simulated_characters_state": characters_state,
            }
        )
    )

    print_step("Move Player")
    print(
        place_character.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
                "new_scenario_id": "scenario_002",
            }
        )
    )

    print_step("Place Lia in scenario")
    print(
        place_character.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_001",
                "new_scenario_id": "scenario_002",
            }
        )
    )

    print_step("Unplace Bran")
    print(
        remove_character_from_scenario.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_002",
            }
        )
    )

    print_step("Final State")
    print(
        list_characters.invoke(
            {
                "simulated_characters_state": characters_state,
                "list_identity": True,
                "list_physical": True,
                "list_narrative": True,
            }
        )
    )

    print_step("Filter By Gender")
    print(
        list_characters.invoke(
            {
                "simulated_characters_state": characters_state,
                "attribute_to_filter": "gender",
                "value_to_match": "female",
            }
        )
    )

    print_step("Player Details")
    print(
        get_player_details.invoke(
            {
                "simulated_characters_state": characters_state,
            }
        )
    )

    print_step("Character Details")
    print(
        get_character_details.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_001",  # Get details for Lia
            }
        )
    )

    print_step("Modify Player Identity")
    print(
        modify_identity.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
                "new_full_name": "Arin the Hero",
            }
        )
    )

    print_step("Append Player Knowledge")
    print(
        modify_knowledge.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
                "new_acquired_knowledge": ["secret treasure location"],
                "append_acquired_knowledge": True,
            }
        )
    )

    print_step("Append Lia Narrative Purpose")
    print(
        modify_narrative.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_001",
                "new_narrative_purposes": [
                    NarrativePurposeModel(mission="sell goods", is_hidden=False)
                ],
                "append_narrative_purposes": True,
            }
        )
    )

    print_step("Attempt Modify Player Dynamic (should fail)")
    print(
        modify_dynamic_state.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
                "new_current_emotion": "excited",
            }
        )
    )

    print_step("Attempt Modify Player Narrative (should fail)")
    print(
        modify_narrative.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
                "new_narrative_role": "protagonist",
            }
        )
    )

    print_step("Attempt Delete Player (should fail)")
    print(
        delete_character.invoke(
            {
                "simulated_characters_state": characters_state,
                "character_id": "character_003",
            }
        )
    )

    print_step("List Character by scenario")
    print(
        list_characters_by_scenario.invoke(
            {
                "simulated_characters_state": characters_state,
            }
        )
    )

    for cid, char in characters_state.simulated_characters.items():
        print(f"\nID: {cid}")
        print(char.model_dump_json(indent=2))

