import json
from typing import AsyncGenerator

# Your actual project imports would go here
from simulated.singleton import SimulatedGameStateSingleton
from core_game.game_event.domain import BaseGameEvent, NarratorInterventionEvent, NPCConversationEvent, PlayerNPCConversationEvent
from subsystems.game_events.dialog_engine.dialog_generator.npc import generate_npc_message_stream
from subsystems.game_events.dialog_engine.dialog_generator.player import generate_player_message_stream
from subsystems.game_events.dialog_engine.dialog_generator.narrator import generate_narrator_message_stream
from subsystems.game_events.dialog_engine.dialog_generator.choice_driven import generate_choice_driven_message_stream
from api.services.actions import check_and_start_event_triggers

async def generate_narrative_stream(event_id: str) -> AsyncGenerator[str, None]:
    print(f"[STREAM] Starting narrative stream for event_id: {event_id}")
    
    game_state = SimulatedGameStateSingleton.get_instance()
    event_info = game_state.events.get_state().get_current_running_event_info()
    event = game_state.events.get_state().get_current_running_event()

    print(f"[STREAM] event_info: {event_info}")
    print(f"[STREAM] event: {event}")
    if event:
        print(f"[STREAM] event.id: {event.id}")
        print(f"[STREAM] event type: {type(event)}")

    if not event_info or not event:
        error_message = {"type": "error", "content": f"No event is running."}
        print(f"[STREAM] No event running.")
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    if event.id != event_id:
        print(f"[STREAM] Event ID mismatch: requested '{event_id}' but current is '{event.id}'")
        error_message = {"type": "error", "content": f"Current running event has a different id."}
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    # CORREGIDO: isinstance debe aceptar cualquiera de las clases, no TODAS
    if not isinstance(event, (NPCConversationEvent, PlayerNPCConversationEvent, NarratorInterventionEvent)):
        print(f"[STREAM] Invalid event type: {type(event)}")
        error_message = {"type": "error", "content": f"Current running event has not implemented this."}
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    try:
        print(f"[STREAM] Entering event.run loop...")
        async for message_json in event.run(game_state):
            print(f"[STREAM] Emitting message: {message_json[:80]}...")  # Preview only first 80 chars
            yield message_json

        print(f"[STREAM] Event.run completed.")

        # --- 3. Handle Stream Completion ---
        final_status = event.status
        print(f"[STREAM] Final event status: {final_status}")

        check_and_start_event_triggers(game_state)
        new_current_event = game_state.events.get_state().get_current_running_event()

        if final_status == "COMPLETED":
            if new_current_event:
                print(f"[STREAM] Event '{event.id}' completed. New event '{new_current_event.id}' started.")
                follow_up_action = {
                    "type": "START_NARRATIVE_STREAM",
                    "payload": {"event_id": new_current_event.id}
                }
                final_message = {"type": "event_end", "follow_up_action": follow_up_action}
                yield f"data: {json.dumps(final_message)}\n\n"
            else:
                print(f"[STREAM] Event '{event.id}' completed. No new event.")
                final_message = {"type": "event_end", "event_id": event_id}
                yield f"data: {json.dumps(final_message)}\n\n"
        elif final_status == "RUNNING":
            print(f"[STREAM] Event '{event.id}' paused. Waiting for player.")
            final_message = {"type": "event_paused", "event_id": event_id}
            yield f"data: {json.dumps(final_message)}\n\n"
        else:
            print(f"[STREAM] Event '{event.id}' failed with status '{final_status}'.")
            final_message = {"type": "event_failed", "event_id": event_id}
            yield f"data: {json.dumps(final_message)}\n\n"

    except Exception as e:
        print(f"[STREAM] FATAL ERROR in event '{event_id}': {e}")
        error_message = {"type": "error", "content": f"A critical error occurred during the event: {e}"}
        yield f"data: {json.dumps(error_message)}\n\n"
