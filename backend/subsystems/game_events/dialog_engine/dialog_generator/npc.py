import os
from typing import AsyncGenerator, Set, List, Optional, Dict, Any, Union
from simulated.game_state import SimulatedGameState
# Importarías tus clases y funciones reales aquí
from subsystems.game_events.dialog_engine.prompts.context import get_formatted_context, character_to_dict, format_nested_dict
from core_game.narrative.schemas import NarrativeBeatModel
from core_game.map.domain import Scenario
from core_game.character.domain import BaseCharacter, PlayerCharacter, NPCCharacter
from core_game.game_event.schemas import NPCMessage
from core_game.game_event.domain import NarratorInterventionEvent, PlayerNPCConversationEvent, NPCConversationEvent
# --- Configuración del Cliente de OpenAI ---
# Es una buena práctica inicializar el cliente una sola vez.
# La clave de la API se lee de la variable de entorno OPENAI_API_KEY.

import openai
client = openai.AsyncOpenAI()



async def generate_npc_message_stream(
    speaker: NPCCharacter,
    event: Union[NPCConversationEvent, PlayerNPCConversationEvent],
    game_state: SimulatedGameState
) -> AsyncGenerator[str, None]:
    """
    Generates a text stream for a specific character's turn in a conversation.

    This function builds a detailed prompt, calls the LLM, and returns the raw
    text stream of the response, including special tags like [dialogue], [action], etc.
    """

    
    formatted_character = format_nested_dict(character_to_dict(speaker))

    npc_system_prompt = f"""
    You are a role-playing game director, responsible for generating the dialogue and actions for a specific character.
    Your current task is to impersonate and generate the turn for the character: **{speaker.identity.full_name} (ID: {speaker.id})**.
    {formatted_character}
    IMPERSONATE IT THE MOST ACCURATELY YOU CAN
    A "turn" represents the character's entire intervention at this moment. To create a natural, game-like flow, you should break down the character's intervention into multiple, smaller messages using the special tags. Think of each tag as a separate line of text that the player would read before clicking to see the next one.

    IMPORTANT: While a turn can have multiple tags, the content within each `[dialogue]` or `[action]` tag should be a complete thought. Avoid making the messages too short or fragmented. A single message can contain (and mostly should contain) multiple sentences if it makes sense for the character to say them without a pause.

    You must generate a turn that is consistent with the character's personality, the current situation and the conversation history all provided in the user prompt context.

    Ensure the conversation does not deviate much from the 'Dialog Description' provided in the user prompt's context. This description can contain the topic, goal, and tone for the conversation. All dialogue and actions must serve the purpose outlined in the description while also being creative, interesting, evoking and consistent with the character's personality and the conversation history.
    Ensure the intervention is consistent with the conversation history.

    Your goal is to deliver this character's turn, not to end the entire conversation. Your intervention should feel like one part of a larger dialogue. Conclude your character's immediate thoughts or actions, but leave the overall conversation open for others to respond to, unless your turn naturally provides a definitive conclusion to the event's goal.

    Your response MUST use the following special tags:
    - `[dialogue]` to indicate spoken words.
    - `[action]` to describe a physical action the character performs.
    
    A turn can contain multiple tags. For example: `[dialogue] I don't believe you. [action] Narrows their eyes. [dialogue] Show me the proof.`
    
    It is crucial that every response you generate MUST end with the `[end]` tag to signify the character has finished their turn.

    Below are examples of desired responses. These are guides for structure, not rigid answers. Be creative and vary the number of messages, their length, and their order, tone to fit the specific moment in the narrative.

    **Example 1**
    [dialogue] I've heard the rumors, you know. They say you weren't at your post when the gate was breached.
    [action] Takes a slow, deliberate step forward, hand resting on the hilt of their sword.
    [dialogue] I want to hear it from you. Is it true?
    [end]
    ---
    **Example 2**
    [action] Fidgets with the strap of their bag, avoiding eye contact.
    [dialogue] The artifact... yes, I know where it is. But getting to it won't be easy. The area is swarming with patrols, more than I've ever seen. We'll need a distraction. A big one.
    [end]
    ---
    **Example 3**
    [action] Slowly draws a dagger from their boot, the metal glinting in the dim light.
    [action] Places the dagger on the table between them, spinning it gently.
    [dialogue] Now... let's talk about what you really saw that night.
    [end]
    ---
    **Example 4**
    [action] Kicks the heavy oak door open without a word, revealing the darkened hall beyond.
    [end]
    ---
    **Example 5**
    [dialogue] You don't understand what's at stake here. This isn't just about some stolen artifact; it's about the balance of power for the entire region. The Council has been lying to us for years, feeding us stories about prosperity while they hoard resources and let the outer settlements starve. I saw the records with my own eyes, I read the ledgers... it's all a sham designed to keep us weak.
    [end]
    ---
    **Example 6**
    [action] Leans over a dusty table, using a charcoal stick to sketch a rough layout of the enemy encampment on the wood.
    [dialogue] Alright, listen closely. This is our only chance, and everything must be perfect.
    [action] Circles the western wall of the sketch.
    [dialogue] The main assault will come from here, the west. Their defenses are weakest there. That will be loud, chaotic, and it will draw the majority of their forces.
    [action] Taps a second point on the makeshift map, a small, overlooked sewer grate on the eastern side.
    [dialogue] While they're distracted dealing with that, we'll use this old drainage tunnel to slip in unnoticed. It's a long shot, and it'll be tight quarters, but it gets us directly into the command tent.
    [action] Glances up, making eye contact to ensure they are understood.
    [dialogue] Your job is to secure the intel while we keep them busy. That's the primary objective.
    [dialogue] Do not engage unless absolutely necessary. Get in, get the documents, and get out.
    [dialogue] We'll signal you with a bird call when the coast is clear for your exfiltration. Do you understand?
    [end]
    """

    character_ids = set(event.npc_ids)
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

    relations = game_state.read_only_relationships.get_state().get_relationships_for_group(character_ids)

    
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
                {"role": "system", "content": npc_system_prompt},
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