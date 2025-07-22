from enum import Enum
from typing import AsyncGenerator
import json

from core_game.game_event.schemas import (
    CharacterDialogueMessage,
    CharacterActionMessage,
    PlayerThoughtMessage,
    PlayerChoiceMessage,
    PlayerChoiceOptionModel,
    NarratorMessage
)

class InvalidTagError(Exception):
    pass

VALID_TAGS = {"dialogue", "action", "thought", "player_choice", "narrator"}

message_counter = 0

async def parse_and_stream_messages(
    raw_llm_stream: AsyncGenerator[str, None],
    speaker,
    event
) -> AsyncGenerator[str, None]:
    global message_counter

    buffer = ""             # Acumula los chunks que llegan
    current_type = None     # Tag activo ("dialogue", "action", etc.)
    current_id = None       # ID SSE del bloque activo
    content_accum = ""      # Texto acumulado para el bloque activo

    async for chunk in raw_llm_stream:
        buffer += chunk

        while True:
            # --- Caso player_choice: leemos hasta [end] completo ---
            if current_type == "player_choice":
                end_idx = buffer.find("[end]")
                if end_idx == -1:
                    # aún no llegó el cierre
                    break
                choice_block = buffer[:end_idx]
                buffer = buffer[end_idx + len("[end]"):]
                # procesar choice_block igual que antes...
                lines = choice_block.strip().splitlines()
                title = lines[0].strip()
                options = []
                for line in lines[1:]:
                    if line.startswith("(Dialogue)"):
                        options.append(PlayerChoiceOptionModel(
                            type="Dialogue", label=line[len("(Dialogue)"):].strip()))
                    elif line.startswith("(Action)"):
                        options.append(PlayerChoiceOptionModel(
                            type="Action", label=line[len("(Action)"):].strip()))

                message_counter += 1
                current_id = f"msg_{event.id}_{message_counter}"
                event.add_message(PlayerChoiceMessage(
                    actor_id=speaker.id, title=title, options=options))

                yield (
                    "data: " +
                    json.dumps({
                        "message_id": current_id,
                        "type": "player_choice",
                        "speaker_id": speaker.id,
                        "title": title,
                        "options": [o.model_dump() for o in options]
                    }) +
                    "\n\n"
                )

                # cerramos y esperamos siguiente tag
                current_type = None
                content_accum = ""
                continue

            # --- Buscamos un tag completo "[...]" sólo si existe apertura y cierre ---
            open_idx = buffer.find("[")
            close_idx = buffer.find("]", open_idx+1) if open_idx != -1 else -1

            if open_idx != -1 and close_idx != -1:
                # 1) volcamos cualquier texto ANTES del '[' como contenido
                if current_type and open_idx > 0:
                    fragment = buffer[:open_idx]
                    content_accum += fragment
                    yield (
                        "data: " +
                        json.dumps({
                            "message_id": current_id,
                            "type": current_type,
                            "speaker_id": speaker.id,
                            "content": fragment
                        }) +
                        "\n\n"
                    )
                # 2) extraemos el tag completo
                tag = buffer[open_idx+1:close_idx].strip()
                buffer = buffer[close_idx+1:]

                # 3) cerramos el bloque anterior si tocaba
                if current_type and content_accum.strip():
                    event.add_message(_build_message(current_type, speaker, content_accum.strip()))
                content_accum = ""

                # 4) si es [end], terminamos todo
                if tag == "end":
                    return

                # 5) validamos tag
                if tag not in VALID_TAGS:
                    raise InvalidTagError(f"Etiqueta desconocida: [{tag}]")

                # 6) arrancamos un nuevo bloque
                message_counter += 1
                current_id = f"msg_{event.id}_{message_counter}"
                current_type = tag

                yield (
                    "data: " +
                    json.dumps({
                        "message_id": current_id,
                        "type": current_type,
                        "speaker_id": speaker.id,
                        "content": ""
                    }) +
                    "\n\n"
                )
                # Si es player_choice, la próxima iteración entrará en ese caso
                continue

            # --- No hay tag completo: volcamos sólo hasta el '[' si existe ---
            if current_type and buffer:
                next_open = buffer.find("[")
                if next_open != -1:
                    fragment = buffer[:next_open]
                    buffer = buffer[next_open:]
                else:
                    fragment = buffer
                    buffer = ""

                if fragment:
                    content_accum += fragment
                    yield (
                        "data: " +
                        json.dumps({
                            "message_id": current_id,
                            "type": current_type,
                            "speaker_id": speaker.id,
                            "content": fragment
                        }) +
                        "\n\n"
                    )
            break  # salimos del while interno y esperamos más chunks

    # al acabar el stream, finalizamos cualquier texto pendiente
    if current_type and content_accum.strip():
        event.add_message(_build_message(current_type, speaker, content_accum.strip()))


def _build_message(msg_type, speaker, content):
    if msg_type == "dialogue":
        return CharacterDialogueMessage(actor_id=speaker.id, content=content)
    if msg_type == "action":
        return CharacterActionMessage(actor_id=speaker.id, content=content)
    if msg_type == "thought":
        return PlayerThoughtMessage(actor_id=speaker.id, content=content)
    if msg_type == "narrator":
        return NarratorMessage(actor_id="narrator", content=content)
    raise InvalidTagError(f"No se puede crear mensaje para tag {msg_type}")
