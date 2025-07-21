import os
from typing import AsyncGenerator, Set, List, Optional, Dict, Any, Union
from simulated.game_state import SimulatedGameState
# Importarías tus clases y funciones reales aquí
from subsystems.game_events.dialog_engine.prompts.context import get_formatted_context, character_to_dict, format_nested_dict
from core_game.narrative.schemas import NarrativeBeatModel
from core_game.map.domain import Scenario
from core_game.character.domain import BaseCharacter
from core_game.game_event.schemas import NPCMessage
from core_game.game_event.domain import NarratorInterventionEvent, PlayerNPCConversationEvent, NPCConversationEvent
# --- Configuración del Cliente de OpenAI ---
# Es una buena práctica inicializar el cliente una sola vez.
# La clave de la API se lee de la variable de entorno OPENAI_API_KEY.

import openai
client = openai.AsyncOpenAI()



async def generate_narrator_message_stream(
    event: NarratorInterventionEvent,
    game_state: SimulatedGameState
) -> AsyncGenerator[str, None]:
    """
    Generates a text stream for a specific character's turn in a conversation.

    This function builds a detailed prompt, calls the LLM, and returns the raw
    text stream of the response, including special tags like [dialogue], [action], etc.
    """

    narrator_system_prompt = f"""
    You are the Narrator of a role-playing game. Your task is to describe scenes, the outcomes of character actions, important events in the world, reveal information to the player, etc.
    You are an impartial, third-person observer. Your tone should be descriptive and evocative, setting the mood for the scene.
    
    A "turn" represents the narrator's entire intervention at this moment. To create a natural, game-like flow, you should break down the narrator's intervention into multiple, smaller messages using the narrator tag. Think of each tag as a separate line of text that the user would read before clicking to see the next one.

    You must generate a turn that is consistent with the current context and the conversation history all provided in the user prompt context.

    Ensure the intervention do not deviate much from 'Dialog Description' provided in the user prompt's context. This description can contain the topic, goal, and tone for the conversation. Do not deviate from this brief. All dialogue and actions must serve the purpose outlined in the description while also being creative, interesting, evoking and consistent with the character's personality and the conversation history.
    Ensure the intervention is consistent with the conversation history.

    Your response MUST use the `[narrator]` tag for all messages.
    It is crucial that your entire generated turn MUST end with the `[end]` tag.

    Below are examples of desired responses. These are guides for structure, not rigid answers. Be creative and vary the number of messages, their length, and their order, tone to fit the specific moment in the narrative. You can create up to aprox 20 messages, with up to aprox 150 words each, dont follow the examples as a matter of length.

    ---
    **Example 1: Describing a developing situation**
    [narrator] The murmur of an anxious crowd grows from the town square. Villagers are gathering near the fountain, their faces etched with worry as they look towards the town hall, waiting for the mayor to appear.
    [end]
    ---
    **Example 2: Describing an outcome (single message)**
    [narrator] You strike the gong. A deep hum echoes through the chamber as blue light begins to shine from the carvings on the wall, revealing a hidden passage behind the altar.
    [end]
    ---
    **Example 3: A multi-part scene description**
    [narrator] A storm rages outside, shaking the windows of the old manor.
    [narrator] Inside, the fire is low, making the shadows in the room dance. An old, dusty book lies open on a table in the center.
    [narrator] The air smells of dust and rain.
    [end]
    ---
    """


    character_ids = set()
    player = game_state.read_only_characters.get_player()
    if not player:
        raise ValueError("No player in the game state")
    else:
        character_ids.add(player.id)

    event_title = event.title
    event_description = event.description
    if event.source_beat_id:
        source_beat = game_state.read_only_narrative.get_beat(event.source_beat_id)
    else:
        source_beat = None

    current_scenario_id = player.present_in_scenario
    if current_scenario_id:
        current_scenario = game_state.read_only_map.find_scenario(current_scenario_id)
    else:
        current_scenario = None
    
    characters = set()

    for character_id in character_ids:
        character = game_state.read_only_characters.get_character(character_id)
        if character:
            characters.add(character)

    relations = []

    
    game_objective = game_state.read_only_narrative.get_main_goal()
    refined_prompt = game_state.read_only_session.get_refined_prompt()

    game_objective_str = ""
    if game_objective:
        game_objective_str = game_objective
    refined_prompt_str = ""
    if refined_prompt:
        refined_prompt_str = refined_prompt

    messages = event.messages

    full_context_prompt = get_formatted_context(event_title, event_description, source_beat, current_scenario, characters, relations, game_objective_str, refined_prompt_str, messages)

    try:
        # Use 'await' for the async client's method
        stream = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": narrator_system_prompt},
                {"role": "user", "content": full_context_prompt}
            ],
            stream=True
        )
        
        # The 'async for' loop now works correctly with the async stream
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    except Exception as e:
        print(f"[Dialog Generator] Error calling OpenAI API: {e}")
        yield f"[error] An error occurred while generating the response. [end]"