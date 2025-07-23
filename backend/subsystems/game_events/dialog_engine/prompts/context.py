from typing import Optional, List, Set, Dict, Any, Union, Sequence
from core_game.narrative.schemas import NarrativeBeatModel
from core_game.map.domain import Scenario
from core_game.character.domain import BaseCharacter, NPCCharacter
from core_game.game_event.schemas import ConversationMessage, PlayerChoiceMessage, NarratorMessage, PlayerThoughtMessage, CharacterActionMessage, CharacterDialogueMessage
import random

def format_nested_dict(data: Dict[str, Any], indent: int = 0) -> List[str]:
    """Pretty-prints a nested dictionary with clean indentation."""
    lines: List[str] = []
    indent_str = "    " * indent

    for key, value in data.items():
        display_key = str(key).replace("_", " ").capitalize()
        if isinstance(value, dict):
            lines.append(f"{indent_str}{display_key}:")
            lines.extend(format_nested_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{indent_str}{display_key}:")
            if not value:
                lines.append(f"{indent_str}    (None)")
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}    -")
                        lines.extend(format_nested_dict(item, indent + 2))
                    else:
                        lines.append(f"{indent_str}    - {item}")
        elif value is None or value == "":
            lines.append(f"{indent_str}{display_key}: (None)")
        else:
            lines.append(f"{indent_str}{display_key}: {value}")

    return lines

def character_to_dict(character: BaseCharacter) -> Dict[str, Any]:
    """
    Converts a character domain object into a dictionary containing the most
    relevant information for a dialogue prompt.
    """
    # Using .model_dump() is a clean way to get data from Pydantic models
    char_dict = {

        "Identity": character.identity.model_dump(),
        "Psychological": character.psychological.model_dump(),
        "Knowledge": character.knowledge.model_dump()
    }
    # Add dynamic state only for NPCs, as it's crucial for their current behavior
    if isinstance(character, NPCCharacter):
        char_dict["Dynamic State"] = character.dynamic_state.model_dump()
        char_dict["Narrative Weight"] = character.narrative.model_dump()
    return char_dict

def get_end_conversation_message(messages: Sequence[ConversationMessage]) -> str:
    n = len(messages)

    # Umbrales y mensajes
    thresholds = [
        (7,  "You should start driving the conversation into an end"),
        (13, "You must drive the conversation into an end"),
        (20, "You have to drive the conversation into a conclusion. END THE CONVERSATION IMMEDIATELY"),
    ]
    abrupt_msg = "YOU MUST END THE CONVERSATION IMMEDIATELY IN THIS TURN EVEN IF IT ENDS ABRUPTLY"

    # 0) Si superamos 24, devolvemos siempre el mensaje abrupto
    if n > 24:
        return abrupt_msg

    candidates = []
    weights    = []

    # 1) Desde 0 hasta 10 turnos: posibilidad de no empujar al final ("")
    if n <= 10:
        candidates.append("")
        weights.append(10 - n + 1)  # n=0→11, n=10→1

    # 2) Mensajes de umbral según se superen
    for th, msg in thresholds:
        if n > th:
            candidates.append(msg)
            weights.append(n - th)

    # 3) Incluir “abrupt” (pero sólo si n > 20 y < 25)
    if 20 < n <= 24:
        candidates.append(abrupt_msg)
        weights.append(n - 20)

    # Si no hay candidatos (mínimo), devolvemos cadena vacía
    if not candidates:
        return ""

    # Selección ponderada
    return random.choices(candidates, weights=weights, k=1)[0]

def get_formatted_context(event_title: str, event_description: str, source_beat: Optional[NarrativeBeatModel], scenario: Optional[Scenario], characters: Set[BaseCharacter], relations: List[Dict[str, Any]], game_objective: str, refined_prompt: str, messages: Sequence[ConversationMessage]) -> str:

    source_beat_str = ""
    if source_beat:
        source_beat_str = source_beat_str = f"""
        ## Broader Narrative Context:
        This dialogue is a key scene within a larger story unit called a "narrative beat".

        - **Beat Name:** "{source_beat.name}"
        - **Beat's description, goal, etc:** {source_beat.description}
        """

    scenario_str = ""
    if scenario:
        scenario_str = f"""
        ## Setting:
        This dialogue is taking place in the following location:

        - **Scenario Name:** "{scenario.name}"
        - **Visual Description:** {scenario.visual_description}
        - **Narrative Context (Story significance):** {scenario.narrative_context}
        """

    characters_str_list = ["## Characters info:"]
    sorted_characters = sorted(list(characters), key=lambda c: c.id)
    character_name_map = {char.id: char.identity.full_name for char in sorted_characters}
    for char in sorted_characters:
        char_type_str = char.type
        characters_str_list.append(f"\n### Character: Name: {char.identity.full_name} (ID: {char.id}) [Type of character: {char_type_str}]")
        char_data_dict = character_to_dict(char)
        formatted_lines = format_nested_dict(char_data_dict, indent=1)
        characters_str_list.extend(formatted_lines)
    
    characters_str = "\n".join(characters_str_list)

    relations_str = ""
    if relations:
        relations_str_list = ["\n## Character Relationships:"]
        for rel in relations:
            line = (
                f"- {rel['source_id']} -> {rel['type']}, "
                f"Intensity: {rel['intensity']} -> {rel['target_id']}"
            )
            relations_str_list.append(line)
        relations_str = "\n".join(relations_str_list)

    general_game_context_str = f"""
    ## General Game Context
    - **Overall Narrative:** {refined_prompt}
    - **Player's Main Goal in the game:** {game_objective}
    """


     # --- Conversation History Formatting ---
    conversation_history_str_list = ["\n## Conversation History"]
    if not messages:
        conversation_history_str_list.append("This is the first turn of the conversation.")
    else:
        conversation_history_str_list.append("The last few lines of the conversation were:")
        for msg in messages[-35:]:
            speaker_name = f"{character_name_map.get(msg.actor_id, "")}  ({msg.actor_id})"
            
            # Use isinstance for robust type checking
            if isinstance(msg, PlayerChoiceMessage):
                options_str = "\n".join([f"      - ({opt.type}) {opt.label}" for opt in msg.options])
                line = f'{speaker_name} was presented with the choice "{msg.title}" and the following options:\n{options_str}'
            elif isinstance(msg, CharacterDialogueMessage):
                line = f'{speaker_name} said: "{msg.content}"'
            elif isinstance(msg, CharacterActionMessage):
                line = f'{speaker_name} did: "{msg.content}"'
            elif isinstance(msg, PlayerThoughtMessage):
                line = f'{speaker_name} thought: "{msg.content}"'
            elif isinstance(msg, NarratorMessage):
                line = f'Narrator: "{msg.content}"'
            else: # Fallback for any other message types
                line = f'{speaker_name} ({msg.type}): "{msg.content}"'
            
            conversation_history_str_list.append(f"- {line}")
    conversation_history_str = "\n".join(conversation_history_str_list)


    end_conversation_message=get_end_conversation_message(messages)

    context_prompt = f"""
    #Context available:

    ##Current interaction:

    Dialog Title: {event_title}
    Dialog Description: {event_description}
    {source_beat_str}
    {scenario_str}
    {characters_str}
    {relations_str}
    {general_game_context_str}
    
    This is the most important information:
    {conversation_history_str}

    ##Other rellevant info:
    Number of messages: {len(messages)}, 
    {end_conversation_message}
    """
    print("Number of messages: ", len(messages))

    return context_prompt
