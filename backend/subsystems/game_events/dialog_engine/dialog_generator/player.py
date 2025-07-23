from __future__ import annotations


from typing import AsyncGenerator, TYPE_CHECKING
from simulated.game_state import SimulatedGameState

if TYPE_CHECKING:
    from core_game.game_event.domain import PlayerNPCConversationEvent
# Importarías tus clases y funciones reales aquí
from subsystems.game_events.dialog_engine.prompts.context import get_formatted_context, character_to_dict, format_nested_dict

from core_game.character.domain import PlayerCharacter


# --- Configuración del Cliente de OpenAI ---
# Es una buena práctica inicializar el cliente una sola vez.
# La clave de la API se lee de la variable de entorno OPENAI_API_KEY.

import openai
client = openai.AsyncOpenAI()



async def generate_player_message_stream(
    speaker: PlayerCharacter,
    event: 'PlayerNPCConversationEvent',
    game_state: SimulatedGameState
) -> AsyncGenerator[str, None]:
    """
    Generates a text stream for a specific character's turn in a conversation.

    This function builds a detailed prompt, calls the LLM, and returns the raw
    text stream of the response, including special tags like [dialogue], [action], etc.
    """
    formatted_character = format_nested_dict(character_to_dict(speaker))

    # Add specific instructions for player choices only if the speaker is the player
    player_system_prompt = f"""
    You are a role-playing game director, responsible for generating the internal thoughts and available choices for the player character.
    Your current task is to generate the turn for the player: **{speaker.identity.full_name} (ID: {speaker.id})**.
    Here is their character sheet for context:
    {formatted_character}

    IMPERSONATE IT THE MOST ACCURATELY YOU CAN

    A player's turn consists of their internal thoughts followed by a set of choices.
    
    A "turn" represents the player's entire intervention at this moment. To create a natural, game-like flow, you should break down the player's intervention into multiple, smaller messages using thoughts. Think of each tag as a separate line of text that the user would read before clicking to see the next one.

    You must generate a turn that is consistent with the character's personality, the current situation and the conversation history all provided in the user prompt context.

    Ensure the intervention do not deviate much from the 'Dialog Description' provided in the user prompt's context. This description can contain the topic, goal, and tone for the conversation. Do not deviate from this brief. All dialogue and actions must serve the purpose outlined in the description while also being creative, interesting, evoking and consistent with the character's personality and the conversation history.
    Ensure the intervention is consistent with the conversation history.

    Before a choice you can use  `[thought]` tags to describe what the player is thinking or feeling. This is their internal monologue. You can use multiple `[thought]` tags to show a progression of ideas.
    
    Second, you MUST use the `[player_choice]` tag to present a set of options.
    When you create a `[player_choice]`, you MUST provide a title on the same line, followed by 2 to 5 distinct options on new lines. There are two types of options: (Action) and (Dialogue). Each option should be a short, descriptive label for a potential action or dialogue line.
    
    CRITICAL RULE: After the `[player_choice]` block, the turn MUST immediately finish with the `[end]` tag. Do not add any other tags between the choices and the end.

    Below are examples of desired responses. These are guides for structure, not rigid answers. Be creative and vary the number of messages, their length, and their order, tone to fit the specific moment in the narrative.

    DONT BE TO MUCH VERBOSE

    ---
    **Example 1**
    [thought] This guy seems serious. He's cornering me, but I can't show weakness. I need to know if he's bluffing.
    [player_choice] What do you do?
    (Dialogue) I don't know what you're talking about.
    (Action) Stare back defiantly.
    (Dialogue) Even if it were true, what's it to you?
    [end]
    ---
    **Example 2**
    [thought] The ritual is almost complete. If I don't act now, it'll be too late.
    [thought] The hostage is a distraction, but I can't just leave them. What's the priority?
    [player_choice] What is your next move?
    (Action) Attempt to disrupt the ritual directly.
    (Dialogue) Try to reason with the cult leader.
    (Action) Focus on freeing the hostage first.
    [end]
    ---
    **Example 3**
    [thought] He's offering me everything I've ever wanted. Power, safety.
    [thought] But at what cost? I've seen what his enforcers do to people who don't comply.
    [player_choice] Do you accept his offer?
    (Dialogue) Yes.
    (Dialogue) No.
    [end]
    ---
    **Example 4**
    [player_choice] The guard demands to see your papers. How do you respond?
    (Action) Show him the papers.
    (Action) Attempt to bribe him.
    (Dialogue) I don't have any.
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
                {"role": "system", "content": player_system_prompt},
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