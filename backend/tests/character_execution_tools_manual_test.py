import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulated.singleton import SimulatedGameStateSingleton
from subsystems.agents.map_handler.tools.map_tools import create_scenario
from subsystems.agents.character_handler.tools.character_tools import (
    create_npc,
    create_player,
    place_character,
    remove_character_from_scenario,
    delete_character,
    list_characters,
    get_player_details,
    get_character_details,
    modify_identity,
    modify_knowledge,
    modify_dynamic_state,
    modify_narrative,
    list_characters_by_scenario,
)
from core_game.character.schemas import (
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    NarrativePurposeModel,
    KnowledgeModel,
    DynamicStateModel,
)


def print_step(title: str) -> None:
    print(f"\n=== {title.upper()} ===")


def call(tool, **kwargs):
    common = {
        "messages_field_to_update": "messages",
        "logs_field_to_update": "logs",
        "tool_call_id": "manual",
    }
    return tool.invoke({**common, **kwargs})


if __name__ == "__main__":
    SimulatedGameStateSingleton.reset_instance()
    state = SimulatedGameStateSingleton.get_instance()

    # Ensure scenarios exist for placement
    call(
        create_scenario,
        name="Village Square",
        narrative_context="Central hub",
        visual_description="A busy square",
        visual_prompt="village square",
        summary_description="Center of the village",
        indoor_or_outdoor="outdoor",
        type="town",
        zone="village",
    )
    call(
        create_scenario,
        name="Forest Path",
        narrative_context="Shady path",
        visual_description="Trees all around",
        visual_prompt="forest path",
        summary_description="Path into the woods",
        indoor_or_outdoor="outdoor",
        type="forest",
        zone="woods",
    )

    print_step("Create Characters")
    call(
        create_npc,
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
            visual_prompt=(
                "Short woman with sharp eyes wearing travel garb and carrying a ledger."
            ),
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
        knowledge=KnowledgeModel(),
        dynamic_state=DynamicStateModel(),
    )

    call(
        create_npc,
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
            visual_prompt=(
                "Tall and muscular guard in uniform wielding a halberd, scar across left cheek."
            ),
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
                NarrativePurposeModel(mission="defend town", is_hidden=False),
                NarrativePurposeModel(mission="investigate bandits", is_hidden=True),
            ],
        ),
        knowledge=KnowledgeModel(),
        dynamic_state=DynamicStateModel(),
    )

    print_step("Create Player")
    call(
        create_player,
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
            visual_prompt=(
                "Lean and quick wanderer in travel gear carrying a map and lute, tattooed arms visible."
            ),
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
        scenario_id="scenario_001",
    )

    print_step("Move Player")
    call(place_character, character_id="character_003", new_scenario_id="scenario_002")

    print_step("Place Lia in scenario")
    call(place_character, character_id="character_001", new_scenario_id="scenario_002")

    print_step("Unplace Bran")
    call(remove_character_from_scenario, character_id="character_002")

    print_step("Final State")
    call(list_characters, list_identity=True, list_physical=True, list_narrative=True)

    print_step("Filter By Gender")
    call(list_characters, attribute_to_filter="gender", value_to_match="female")

    print_step("Filter By Name Contains")
    call(list_characters, attribute_to_filter="name_contains", value_to_match="the")

    print_step("Player Details")
    call(get_player_details)

    print_step("Character Details")
    call(get_character_details, character_id="character_001")

    print_step("Modify Player Identity")
    call(modify_identity, character_id="character_003", new_full_name="Arin the Hero")

    print_step("Append Player Knowledge")
    call(
        modify_knowledge,
        character_id="character_003",
        new_acquired_knowledge=["secret treasure location"],
        append_acquired_knowledge=True,
    )

    print_step("Append Lia Narrative Purpose")
    call(
        modify_narrative,
        character_id="character_001",
        new_narrative_purposes=[NarrativePurposeModel(mission="sell goods", is_hidden=False)],
        append_narrative_purposes=True,
    )

    print_step("Attempt Modify Player Dynamic (should fail)")
    call(modify_dynamic_state, character_id="character_003", new_current_emotion="excited")

    print_step("Attempt Modify Player Narrative (should fail)")
    call(modify_narrative, character_id="character_003", new_narrative_role="protagonist")

    print_step("Attempt Delete Player (should fail)")
    call(delete_character, character_id="character_003")

    print_step("List Character by scenario")
    call(list_characters_by_scenario)

    for cid, char in state._read_characters.get_state()._working_state.registry.items():
        print(f"\nID: {cid}")
        print(char.model_dump_json(indent=2))

