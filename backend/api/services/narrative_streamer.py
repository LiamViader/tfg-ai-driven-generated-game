# Este código iría en un nuevo archivo, por ejemplo:
# api/services/narrative_streamer.py

import asyncio
import json
import random
from typing import AsyncGenerator, Dict, Any

# Importarías tus modelos y estado de juego reales aquí
from simulated.singleton import SimulatedGameStateSingleton
from core_game.game_event.domain import BaseGameEvent, DialogueEvent # Suponiendo que tienes estos modelos

# --- Simulación de un proveedor de LLM ---
# En un caso real, esto llamaría a la API de OpenAI, Anthropic, etc.
async def get_llm_response_stream(prompt: str) -> AsyncGenerator[str, None]:
    """
    Simula una llamada a un LLM que devuelve un stream de texto.
    """
    print("--- INICIO DEL PROMPT PARA EL LLM ---")
    print(prompt)
    print("--- FIN DEL PROMPT PARA EL LLM ---")

    responses = [
        '[dialogue] Vaya, no esperaba encontrarte aquí... [action] Mira a su alrededor, nervioso. [dialogue] ¿Has visto a alguien más? [end]',
        '[action] Coge una manzana de la mesa y le da un mordisco ruidoso. [dialogue] ¿Querías algo? Porque estoy algo ocupado. [end]',
        '[dialogue] Silencio. [action] Te mira fijamente, intentando leer tu expresión. [end]'
    ]
    full_response = random.choice(responses)
    
    # Simula el streaming palabra por palabra
    for word in full_response.split(' '):
        yield word + " "
        await asyncio.sleep(0.08) # Pausa para simular la generación

# --- Lógica principal del Streamer ---

def build_llm_prompt(event: DialogueEvent) -> str:
    """
    Construye el prompt para el LLM basado en el contexto del evento.
    """
    # Aquí es donde reúnes todo el contexto que el LLM necesita.
    game_state = SimulatedGameStateSingleton.get_instance()
    player = game_state.read_only_characters.get_player()
    
    # Ejemplo de construcción de prompt
    prompt = "Eres un director de una escena narrativa en un juego de rol de supervivencia.\n"
    prompt += "Contexto del mundo: Un apocalipsis zombi ha devastado la sociedad.\n"
    prompt += f"Escenario actual: {game_state.map.get_scenario(player.present_in_scenario).name} - {game_state.map.get_scenario(player.present_in_scenario).narrative_context}\n\n"
    prompt += "Personajes en la escena:\n"
    # (Aquí añadirías un bucle para describir a todos los personajes presentes)
    prompt += f"- {player.identity.full_name}: {player.psychological.personality_summary}\n"
    
    prompt += f"\nEl evento actual es: '{event.name}'.\n"
    prompt += f"Descripción del evento: {event.description}\n"
    prompt += "Genera el siguiente turno de la conversación. Usa las etiquetas [dialogue], [action] y termina con [end].\n"
    
    return prompt

async def generate_narrative_stream(event_id: str) -> AsyncGenerator[str, None]:
    """
    Generador principal que produce los eventos JSON para el cliente.
    """
    # 1. Obtener el estado del juego y el evento
    game_state = SimulatedGameStateSingleton.get_instance()
    event = game_state.events.get_state().get_event_by_id(event_id)
    
    if not event or not isinstance(event, DialogueEvent):
        # En un caso real, podrías querer enviar un evento de error.
        print(f"Error: Evento con id '{event_id}' no encontrado o no es un evento de diálogo.")
        return

    # 2. Construir el prompt para el LLM
    prompt = build_llm_prompt(event)
    
    # 3. Obtener el stream del LLM
    llm_stream = get_llm_response_stream(prompt)
    
    # 4. Procesar el stream y enviarlo al cliente en formato SSE
    buffer = ""
    current_type = "dialogue"
    # (En un sistema real, el TurnManager decidiría quién habla)
    character_id = "character_002" 

    async for chunk in llm_stream:
        buffer += chunk
        
        # Lógica de parsing para buscar tokens especiales
        found_token = None
        if "[dialogue]" in buffer: found_token = "[dialogue]"
        elif "[action]" in buffer: found_token = "[action]"
        elif "[end]" in buffer: found_token = "[end]"

        if found_token:
            parts = buffer.split(found_token, 1)
            content_before = parts[0]
            
            if content_before.strip():
                message = {"type": current_type, "character_id": character_id, "content": content_before}
                yield f"data: {json.dumps(message)}\n\n"

            if found_token == "[end]":
                end_message = {"type": "end_turn", "character_id": None, "content": None}
                yield f"data: {json.dumps(end_message)}\n\n"
                # Marcar el evento como completado en el estado del juego
                game_state.events.get_state().complete_event(event.id)
                return # Finaliza el stream

            current_type = found_token.strip('[]')
            buffer = parts[1]
    
    # Si el stream del LLM termina sin un [end], nos aseguramos de enviar lo que queda.
    if buffer.strip():
        final_message = {"type": current_type, "character_id": character_id, "content": buffer}
        yield f"data: {json.dumps(final_message)}\n\n"
        
    # Y enviamos un evento de finalización como fallback.
    fallback_end_message = {"type": "end_turn", "character_id": None, "content": None}
    yield f"data: {json.dumps(fallback_end_message)}\n\n"

