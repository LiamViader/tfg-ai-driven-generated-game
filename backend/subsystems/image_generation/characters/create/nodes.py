import asyncio
from typing import cast
from .schemas import GraphState
from .character_processor.orchestrator import get_character_processor_graph_app
from .character_processor.schemas import CharacterProcessorState

async def process_all_characters_node(state: GraphState) -> dict:
    print("--- 🚀 Starting to process all characters in parallel ---")
    processor_app = get_character_processor_graph_app()

    tasks = [
        processor_app.ainvoke(
            CharacterProcessorState(
                character=char,
                graphic_style=state.graphic_style,
                general_game_context=state.general_game_context,
            )
        )
        for char in state.characters
    ]

    results = await asyncio.gather(*tasks)

    successful = []
    failed = []
    for res in results:
        char_state = CharacterProcessorState(**res)
        if char_state.error is None and char_state.image_base64 is not None:
            successful.append(char_state)
        else:
            failed.append(char_state)

    print(f"  - Results: {len(successful)} success(es), {len(failed)} failure(s).")
    return {"successful_characters": successful, "failed_characters": failed}
