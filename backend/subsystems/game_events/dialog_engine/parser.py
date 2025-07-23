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

    buffer = ""
    current_type = None
    current_id = None
    content_accum = ""

    async for chunk in raw_llm_stream:
        buffer += chunk

        while True:
            # Si estamos en player_choice, esperamos hasta encontrar el cierre [end]
            if current_type == "player_choice":
                end_idx = buffer.find("[end]")
                if end_idx == -1:
                    break  # aún no llegó todo
                choice_block = buffer[:end_idx].strip()
                buffer = buffer[end_idx + len("[end]"):]
                
                # Procesamos y emitimos solo un mensaje con título + opciones
                lines = choice_block.splitlines()
                title = lines[0].strip()
                options = []
                for line in lines[1:]:
                    line = line.strip()
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

                yield "data: " + json.dumps({
                    "message_id": current_id,
                    "type": "player_choice",
                    "speaker_id": speaker.id,
                    "title": title,
                    "options": [o.model_dump() for o in options]
                }) + "\n\n"

                # Listo, volvemos a esperar el siguiente tag
                current_type = None
                content_accum = ""
                continue

            # Buscamos un tag completo "[...]" — solo si tenemos '[' y ']' en el buffer
            open_idx = buffer.find("[")
            close_idx = buffer.find("]", open_idx + 1) if open_idx != -1 else -1

            if open_idx != -1 and close_idx != -1:
                # 1) Emitimos cualquier texto ANTES del tag como fragmento de contenido
                if current_type and open_idx > 0:
                    fragment = buffer[:open_idx]
                    content_accum += fragment
                    yield "data: " + json.dumps({
                        "message_id": current_id,
                        "type": current_type,
                        "speaker_id": speaker.id,
                        "content": fragment
                    }) + "\n\n"

                # 2) Extraemos el nombre del tag
                tag = buffer[open_idx+1:close_idx].strip()
                buffer = buffer[close_idx+1:]

                # 3) Cerramos el bloque anterior si había contenido acumulado
                if current_type and content_accum.strip():
                    event.add_message(_build_message(current_type, speaker, content_accum.strip()))
                content_accum = ""

                # 4) Si es [end], terminamos la función
                if tag == "end":
                    return

                # 5) Validamos que sea un tag conocido
                if tag not in VALID_TAGS:
                    raise InvalidTagError(f"Etiqueta desconocida: [{tag}]")

                # 6) Arrancamos un nuevo bloque
                message_counter += 1
                current_id = f"msg_{event.id}_{message_counter}"
                current_type = tag

                # ** Solo para player_choice NO emitimos aquí un mensaje vacío**
                if tag != "player_choice":
                    yield "data: " + json.dumps({
                        "message_id": current_id,
                        "type": current_type,
                        "speaker_id": speaker.id,
                        "content": ""
                    }) + "\n\n"
                continue

            # 7) Si no hay un tag completo, volcamos texto hasta el próximo '[' (o todo)
            if current_type and buffer:
                next_open = buffer.find("[")
                if next_open != -1:
                    fragment = buffer[:next_open]
                    buffer = buffer[next_open:]
                else:
                    fragment = buffer
                    buffer = ""
                content_accum += fragment
                yield "data: " + json.dumps({
                    "message_id": current_id,
                    "type": current_type,
                    "speaker_id": speaker.id,
                    "content": fragment
                }) + "\n\n"
            break  # salimos del while y esperamos más chunks

    # Al terminar el stream, añadimos el bloque final si queda contenido
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
