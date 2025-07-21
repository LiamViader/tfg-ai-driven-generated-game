from __future__ import annotations


from typing import AsyncGenerator, Set, List, Optional, Dict, Any, Union, TYPE_CHECKING
from simulated.game_state import SimulatedGameState

if TYPE_CHECKING:
    from core_game.game_event.domain import PlayerNPCConversationEvent
from simulated.game_state import SimulatedGameState

from core_game.character.domain import BaseCharacter, PlayerCharacter
from subsystems.game_events.dialog_engine.prompts.context import get_formatted_context, character_to_dict, format_nested_dict

# --- OpenAI Client Setup ---
import openai
client = openai.AsyncOpenAI()


async def generate_choice_driven_message_stream(
    player_choice: str,
    speaker: PlayerCharacter,
    event: 'PlayerNPCConversationEvent',
    game_state: SimulatedGameState
) -> AsyncGenerator[str, None]:
    """
    Generates an NPC's reaction stream based on a specific choice made by the player.

    This function builds a prompt that emphasizes the player's action and instructs the LLM
    to generate a direct and coherent response from the specified NPC.
    """

    event_title = event.title
    event_description = event.description
    # ... and so on for source_beat, scenario, characters, relations, etc.
    
    
    # 2. Create the specific system prompt for this task
    formatted_character = "\n".join(format_nested_dict(character_to_dict(speaker)))
            
    context_prompt = f"""
    #PLAYER HAS MADE A CHOICE, YOU MUST DEVELOP HIS CHOICE:
    The player character, {speaker.identity.full_name}, has just decided to perform the following option: "{player_choice}"
    
    Now, generate the full intervention for {speaker.identity.full_name} as they carry out this choice.
    """
    
    formatted_character = "\n".join(format_nested_dict(character_to_dict(speaker)))
            
    system_prompt = f"""
    You are a role-playing game director. Your task is to expand a player's chosen action label into a full, in-character turn.
    You MUST impersonate the player character: **{speaker.identity.full_name} (ID: {speaker.id})**.
    Here is their character sheet for context:
    {formatted_character}
    
    CRITICAL INSTRUCTION: The user will provide a short label describing a choice the player made (e.g., "(Dialogue) Ask about the rumors"). Your task is to generate a full turn that executes this choice, consistent with the player character's personality. The generated turn must strictly adhere to the intent of the player's choice.

    A "turn" represents the character's entire intervention at this moment. To create a natural, game-like flow, you should break down the character's intervention into multiple, smaller messages using the special tags. Think of each tag as a separate line of text that the player would read before clicking to see the next one.

    IMPORTANT: While a turn can have multiple tags, the content within each `[dialogue]` or `[action]` tag should be a complete thought. Avoid making the messages too short or fragmented. A single message can contain (and mostly should contain) multiple sentences if it makes sense for the character to say them without a pause.

    You must generate a turn that is consistent with the character's personality, the current situation and the conversation history all provided in the user prompt context.
    Ensure the intervention is consistent with the conversation history.
    
    Your goal is to deliver this character's turn, not to end the entire conversation. Your intervention should feel like one part of a larger dialogue. Conclude your character's immediate thoughts or actions, but leave the overall conversation open for others to respond to, unless your turn naturally provides a definitive conclusion to the event's goal.

    Your response MUST use the following special tags:
    - `[dialogue]` to indicate spoken words.
    - `[action]` to describe a physical action the character performs.
    
    Your entire generated turn MUST end with the `[end]` tag.

    Examples of how to expand a player choice:

    ---
    **IF Player Choice was:** (Dialogue) "I don't know what you're talking about."
    **Your generated response could be:**
    [action] Shakes their head, putting on a confused expression.
    [dialogue] Rumors? I'm afraid I don't know what you're talking about. I just arrived in town.
    [end]
    ---
    **IF Player Choice was:** (Action) Attempt to bribe him.
    **Your generated response could be:**
    [action] Discreetly pulls a small pouch of coins from their belt, keeping it low.
    [dialogue] Perhaps there's been a misunderstanding. I'm sure we can come to an arrangement that benefits us both.
    [action] Jangles the pouch lightly.
    [end]
    ---
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

    full_context_prompt = get_formatted_context(event_title, event_description, source_beat, current_scenario, characters, relations, game_objective_str, refined_prompt_str, messages) + context_prompt

    try:
        # Use 'await' for the async client's method
        stream = await client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
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

