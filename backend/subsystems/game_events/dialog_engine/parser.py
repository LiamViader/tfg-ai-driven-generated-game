from __future__ import annotations


from typing import AsyncGenerator,  TYPE_CHECKING, Union

if TYPE_CHECKING:
    from core_game.game_event.domain import BaseGameEvent, NPCConversationEvent, PlayerNPCConversationEvent, NarratorInterventionEvent

import json


# --- Your actual project imports ---

from core_game.character.domain import BaseCharacter
# --- Import the new, specific message schemas ---
from core_game.game_event.schemas import (
    CharacterDialogueMessage,
    CharacterActionMessage,
    PlayerThoughtMessage,
    PlayerChoiceMessage,
    PlayerChoiceOptionModel,
    NarratorMessage
)

# --- Define the valid tags our system understands ---
VALID_TAGS = {"dialogue", "action", "thought", "player_choice", "narrator"}

# --- Custom exception for parsing errors ---
class InvalidTagError(Exception):
    """Raised when the LLM returns an unknown tag or text before the first tag."""
    pass

# A simple counter to give each message block a unique ID within the event
message_counter = 0

async def parse_and_stream_messages(
    raw_llm_stream: AsyncGenerator[str, None],
    speaker: BaseCharacter,
    event: Union['NPCConversationEvent', 'PlayerNPCConversationEvent', 'NarratorInterventionEvent']
) -> AsyncGenerator[str, None]:
    """
    Consumes a raw text stream from an LLM, parses it for special tags,
    updates the game state with typed message objects, and yields structured
    JSON messages for the client.
    """
    global message_counter
    buffer = ""
    content_buffer = ""
    current_type = None 
    current_message_id = None
    is_first_message = True

    async for chunk in raw_llm_stream:
        buffer += chunk
        
        while True:
            start_bracket = buffer.find('[')
            end_bracket = buffer.find(']')

            if start_bracket != -1 and end_bracket != -1 and start_bracket < end_bracket:
                # --- We found a potential tag ---
                
                text_before_tag = buffer[:start_bracket]

                if is_first_message and text_before_tag.strip():
                    raise InvalidTagError(f"Received text ('{text_before_tag.strip()}') before the first tag. The stream must start with a tag.")

                if text_before_tag:
                    content_buffer += text_before_tag
                    message_chunk = {
                        "message_id": current_message_id, "type": current_type,
                        "speaker_id": speaker.id, "content": text_before_tag
                    }
                    yield f"data: {json.dumps(message_chunk)}\n\n"

                tag = buffer[start_bracket + 1:end_bracket]
                buffer = buffer[end_bracket + 1:]

                if tag != "end" and tag not in VALID_TAGS:
                    raise InvalidTagError(f"Received an unknown tag from the LLM: '[{tag}]'")

                # --- Finalize the previous message block ---
                if not is_first_message and content_buffer.strip():
                    # Create the appropriate Pydantic model based on the message type
                    if current_type == "dialogue":
                        new_message = CharacterDialogueMessage(actor_id=speaker.id, content=content_buffer.strip())
                    elif current_type == "action":
                        new_message = CharacterActionMessage(actor_id=speaker.id, content=content_buffer.strip())
                    elif current_type == "thought":
                        new_message = PlayerThoughtMessage(actor_id=speaker.id, content=content_buffer.strip())
                    elif current_type == "narrator":
                        new_message = NarratorMessage(actor_id="narrator", content=content_buffer.strip())
                    
                    # Add the structured message object to the event's log
                    event.add_message(new_message)
                
                content_buffer = ""

                if tag == "end":
                    return

                # --- Handle special case: player_choice ---
                if tag == "player_choice":
                    # The player_choice tag is processed as a single block
                    # We need to find the closing [end] tag for the choice block
                    end_choice_marker = buffer.find('[end]')
                    if end_choice_marker == -1:
                        # This is an incomplete stream, we need to wait for more chunks
                        # Put the tag back in the buffer and wait for the next chunk
                        buffer = f"[{tag}]{buffer}"
                        break
                    
                    choice_block_content = buffer[:end_choice_marker].strip()
                    buffer = buffer[end_choice_marker:] # Keep the [end] tag for the next loop iteration

                    lines = choice_block_content.split('\n')
                    title = lines[0].strip()
                    options = []
                    for line in lines[1:]:
                        line = line.strip()
                        if line.startswith("(Dialogue)"):
                            options.append(PlayerChoiceOptionModel(type="Dialogue", label=line.replace("(Dialogue)", "").strip()))
                        elif line.startswith("(Action)"):
                            options.append(PlayerChoiceOptionModel(type="Action", label=line.replace("(Action)", "").strip()))
                    
                    message_counter += 1
                    current_message_id = f"msg_{event.id}_{message_counter}"

                    choice_message = PlayerChoiceMessage(
                        actor_id=speaker.id,
                        title=title,
                        options=options
                    )
                    event.add_message(choice_message)

                    # Send the complete choice block to the client at once
                    client_message = {
                        "message_id": current_message_id, "type": "player_choice",
                        "speaker_id": speaker.id, "title": title,
                        "options": [opt.model_dump() for opt in options]
                    }
                    yield f"data: {json.dumps(client_message)}\n\n"
                    is_first_message = False
                    continue # Continue to the next tag, which should be [end]

                # --- Start a new regular message block ---
                current_type = tag
                message_counter += 1
                current_message_id = f"msg_{event.id}_{message_counter}"

                new_block_message = {
                    "message_id": current_message_id, "type": current_type,
                    "speaker_id": speaker.id, "content": ""
                }
                yield f"data: {json.dumps(new_block_message)}\n\n"
                
                is_first_message = False
            else:
                break
        
        if buffer and not is_first_message:
            content_buffer += buffer
            message_chunk = {
                "message_id": current_message_id, "type": current_type,
                "speaker_id": speaker.id, "content": buffer
            }
            yield f"data: {json.dumps(message_chunk)}\n\n"
            buffer = ""
            
    # Finalize any remaining content when the stream ends
    if content_buffer.strip():
        if current_type == "dialogue":
            new_message = CharacterDialogueMessage(actor_id=speaker.id, content=content_buffer.strip())
        elif current_type == "action":
            new_message = CharacterActionMessage(actor_id=speaker.id, content=content_buffer.strip())
        elif current_type == "thought":
            new_message = PlayerThoughtMessage(actor_id=speaker.id, content=content_buffer.strip())
        elif current_type == "narrator":
            new_message = NarratorMessage(actor_id="narrator", content=content_buffer.strip())
        
        event.add_message(new_message)
