import asyncio
import base64
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from subsystems.image_generation.characters.create.orchestrator import get_created_character_images_generation_app
from subsystems.image_generation.characters.create.schemas import GraphState
from core_game.character.schemas import (
    NonPlayerCharacterModel,
    IdentityModel,
    PhysicalAttributesModel,
    PsychologicalAttributesModel,
    NarrativeWeightModel,
    NarrativePurposeModel,
    KnowledgeModel,
    DynamicStateModel,
)

async def main():
    graph = get_created_character_images_generation_app()
    output_dir = os.path.join('images', 'characters')
    os.makedirs(output_dir, exist_ok=True)

    characters = [
        NonPlayerCharacterModel(
            identity=IdentityModel(
                full_name="Lia the Merchant",
                alias=None,
                age=30,
                gender="female",
                profession="merchant",
                species="human",
                alignment="neutral",
            ),
            physical=PhysicalAttributesModel(
                appearance="Short woman with sharp eyes",
                visual_prompt="Short woman with sharp eyes wearing travel garb",
                distinctive_features=[],
                clothing_style="travel garb",
                characteristic_items=["ledger"],
            ),
            psychological=PsychologicalAttributesModel(
                personality_summary="Shrewd yet kind-hearted",
                personality_tags=["shrewd", "kind"],
                motivations=["profit"],
                values=["fairness"],
                fears_and_weaknesses=[],
                communication_style="direct",
                backstory="Former street orphan",
                quirks=["hums"],
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
        ),
    ]

    result = await graph.ainvoke(
        GraphState(
            characters=characters,
            graphic_style="cartoon",
            general_game_context="a fantasy town",
        )
    )

    final_state = GraphState(**result)
    if final_state.successful_characters:
        char_state = final_state.successful_characters[0]
        if char_state.image_base64:
            img_bytes = base64.b64decode(char_state.image_base64)
            file_name = f"{char_state.character.id}.png"
            with open(os.path.join(output_dir, file_name), "wb") as f:
                f.write(img_bytes)

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: The OPENAI_API_KEY environment variable is not set.")
    else:
        asyncio.run(main())
