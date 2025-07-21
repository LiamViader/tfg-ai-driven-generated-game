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
    """
    The main orchestration service for a narrative event stream.

    This async generator manages the lifecycle of a conversation:
    1. Decides whose turn it is.
    2. Calls the appropriate generator to create the message content.
    3. Parses the stream, updates the game state, and forwards messages to the client.
    """
    game_state = SimulatedGameStateSingleton.get_instance()
    event_info = game_state.events.get_state().get_current_running_event_info()
    event = game_state.events.get_state().get_current_running_event()

    if not event_info or not event:
        error_message = {"type": "error", "content": f"No event is running."}
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    if event.id != event_id:
        error_message = {"type": "error", "content": f"Current running event has a diferent id."}
        yield f"data: {json.dumps(error_message)}\n\n"
        return
    
    if not isinstance(event,NPCConversationEvent) or not isinstance(event,PlayerNPCConversationEvent) or not isinstance(event,NarratorInterventionEvent):
        error_message = {"type": "error", "content": f"Current running event has not implemented this."}
        yield f"data: {json.dumps(error_message)}\n\n"
        return

    try:
        async for message_json in event.run(game_state):
            yield message_json
            
        # --- 3. Handle Stream Completion ---
        # After the event's run() generator finishes, we check the final status of the event.
        final_status = event.status

        check_and_start_event_triggers(game_state)
        new_current_event = game_state.events.get_state().get_current_running_event()

        if final_status == "COMPLETED":
            if new_current_event:
                # A new event has started automatically!
                print(f"[Narrative Streamer] Event '{event.id}' completed, and new event '{new_current_event.id}' has started.")
                follow_up_action = {
                    "type": "START_NARRATIVE_STREAM",
                    "payload": {"event_id": new_current_event.id}
                }
                final_message = {"type": "event_end", "follow_up_action": follow_up_action}
                yield f"data: {json.dumps(final_message)}\n\n"
            else:
                print(f"[Narrative Streamer] Event '{event.id}' completed. Sending end signal.")
                final_message = {"type": "event_end", "event_id": event_id}
                yield f"data: {json.dumps(final_message)}\n\n"
        elif final_status == "RUNNING":
            # This indicates the event has paused for player input.
            print(f"[Narrative Streamer] Event '{event.id}' paused for player choice. Sending pause signal.")
            final_message = {"type": "event_paused", "event_id": event_id}
            yield f"data: {json.dumps(final_message)}\n\n"
        else: # FAILED or other terminal statuses
            print(f"[Narrative Streamer] Event '{event.id}' finished with status '{final_status}'.")
            final_message = {"type": "event_failed", "event_id": event_id}
            yield f"data: {json.dumps(final_message)}\n\n"

    except Exception as e:
        # Catch any unexpected errors during the event's execution.
        print(f"FATAL ERROR during execution of event '{event_id}': {e}")
        error_message = {"type": "error", "content": f"A critical error occurred during the event: {e}"}
        yield f"data: {json.dumps(error_message)}\n\n"
