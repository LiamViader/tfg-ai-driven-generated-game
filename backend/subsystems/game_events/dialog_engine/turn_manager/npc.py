from __future__ import annotations
import os

from typing import AsyncGenerator, Set, List, Optional, Dict, Any, Union, TYPE_CHECKING, cast
from simulated.game_state import SimulatedGameState

if TYPE_CHECKING:
    from core_game.game_event.domain import NPCConversationEvent
from core_game.game_event.activation_conditions.domain import ActivationCondition, CharacterInteractionOption
from subsystems.game_events.dialog_engine.prompts.context import get_formatted_context
from subsystems.game_events.dialog_engine.schemas.payloads import TurnDecision
from core_game.character.domain import BaseCharacter, NPCCharacter
import openai
import json
from pydantic import ValidationError
import time


import openai

client = openai.OpenAI()


def call_llm_with_structured_output(prompt: str, participants: List[str], max_retries: int = 2) -> Optional[str]:
    """
    Calls the OpenAI API to get a structured JSON response for deciding the next speaker.
    Includes a retry mechanism for validation and API errors.

    Args:
        prompt: The fully formatted prompt for the LLM.
        participants: A list of valid character IDs for the LLM to choose from.
        max_retries: The number of times to retry if the call fails.

    Returns:
        The ID of the chosen next speaker, or None if the conversation should end or if all retries fail.
    """

    MAX_TURNS = 20

    # System prompt to instruct the model on the desired output format
    system_prompt = f"""
    You are a narrative director for a role-playing game. Your task is to decide which character should speak next to create the most compelling and logical conversation.
    Use the full context provided in the user prompt—especially to make your decision. For example, a character described as 'talkative' might speak more often, etc. Just make well informed decisions.
    Based on this context, you must choose one of the following valid character IDs: {', '.join(participants)}.
    Speakers typically alternate, but this is not mandatory — the same character may speak again if it feels natural in the flow of conversation or supports the narrative.

    Occasionally, to make the drama more interesting, you can choose a less obvious character to speak next, creating an interruption or a surprising turn, as long as it remains coherent with the narrative.
    
    To end the conversation, set "next_speaker_id" to null. Only do this if the conversation has reached a logical conclusion, meaning the purpose of the event (as described in its description) has been fulfilled and the last message provides a sense of closure. Do not end the conversation prematurely. HOWEVER IN THE CONTEXT YOU MIGHT RECEIVE INDICATIONS ABOUT FINISHING THE CONVERSATION, YOU MUST OBEY THEM.

    You MUST respond with a JSON object containing two keys:
    1. "next_speaker_id": A string containing the exact ID of the character you choose, or null to end the conversation.
    2. "reasoning": A brief explanation for your choice.
    """

    for attempt in range(max_retries):
        try:
            print(f"[LLM] Attempt {attempt + 1}/{max_retries} to decide the next speaker.")
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            response_content = response.choices[0].message.content
            if not response_content:
                print(f"[LLM Validation Error] Attempt {attempt + 1}: The model returned an empty response.")
                continue # Skip to the next retry attempt

            # --- FIX ENDS HERE ---
            # 1. Parse the JSON string from the response
            decision_json = json.loads(response_content)
            
            # 2. Validate the JSON structure with Pydantic
            decision = TurnDecision.model_validate(decision_json)
            
            # 3. Validate the decision
            if decision.next_speaker_id is None:
                print(f"[LLM] Decision successful: End conversation. Reason: {decision.reasoning}")
                return None # The LLM decided to end the conversation
            
            if decision.next_speaker_id in participants:
                print(f"[LLM] Decision successful: '{decision.next_speaker_id}'. Reason: {decision.reasoning}")
                return decision.next_speaker_id
            else:
                print(f"[LLM Validation Error] Attempt {attempt + 1}: The model chose an invalid participant ('{decision.next_speaker_id}').")

        except json.JSONDecodeError:
            print(f"[LLM Validation Error] Attempt {attempt + 1}: The model did not return valid JSON.")
        except ValidationError as e:
            print(f"[LLM Validation Error] Attempt {attempt + 1}: The model's JSON did not match the required schema. Details: {e}")
        except Exception as e:
            print(f"[LLM API Error] Attempt {attempt + 1}: An unexpected error occurred: {e}")

        # Wait a moment before retrying
        if attempt < max_retries - 1:
            time.sleep(1)

    print("[LLM] All retry attempts failed. Could not decide on a next speaker.")
    return None


def decide_next_npc_speaker(event: 'NPCConversationEvent', event_triggered_by: Optional[ActivationCondition],  game_state: SimulatedGameState) -> Optional[NPCCharacter]:
    """
    Decide qué personaje debe hablar a continuación en un evento narrativo.
    Esta función es el núcleo del "Narrative Orchestrator".

    Args:
        event: El objeto del evento de dominio actual.
        game_state: El estado actual del juego para obtener contexto.

    Returns:
        El ID del personaje que debe hablar a continuación, o None si la conversación debe terminar.
    """

    if event_triggered_by and isinstance(event_triggered_by, CharacterInteractionOption) and not event.messages: # primer missatge, i ha sigut triggereat per interactuar amb un npc, te sentit que parli el npc
        character = game_state.read_only_characters.get_character(event_triggered_by.character_id)
        if isinstance(character, NPCCharacter):
            return cast(NPCCharacter, character)
        return None

    # sino que decideixi el llm. mes endavant es podria fer un sistema per regles o random o el que sigui per disminuir latència

    character_ids = set(event.npc_ids)
    player = game_state.read_only_characters.get_player()
    if not player:
        raise ValueError("No player in the game state")
    
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

    prompt = get_formatted_context(event_title, event_description, source_beat, current_scenario, characters, relations, game_objective_str, refined_prompt_str, messages)

    next_speaker_id = call_llm_with_structured_output(prompt, list(character_ids), 3)

    if not next_speaker_id:
        return None

    # --- Validate and Cast the Result ---
    next_speaker_character = game_state.read_only_characters.get_character(next_speaker_id)
    
    if isinstance(next_speaker_character, NPCCharacter):
        return cast(NPCCharacter, next_speaker_character)
    
    return None




