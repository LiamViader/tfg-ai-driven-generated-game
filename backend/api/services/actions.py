from typing import Dict, Any
from api.schemas.responses import ActionResponse, FollowUpAction, FollowUpActionType, StartNarrativeStreamPayload
from simulated.singleton import SimulatedGameStateSingleton
from simulated.game_state import SimulatedGameState
from api.services.game_state import get_incremental_changes
from core_game.game_event.domain import BaseGameEvent
from typing import Optional
from core_game.game_event.activation_conditions.domain import CharacterInteractionOption

def check_and_start_event_triggers(game_state: SimulatedGameState) -> Optional[BaseGameEvent]:
    available_events = game_state.events.get_state().get_events_by_status("AVAILABLE")

    for event in available_events:
        for condition in event.activation_conditions:                    
            if condition.is_met(game_state):
                last_event=event
                game_state.events.get_state().start_event(event.id, condition.id)
                break
    return last_event

def _try_start_character_activation_condition_event(game_state: SimulatedGameState, activation_condition_id: str) -> Optional[BaseGameEvent]:
    available_events = game_state.events.get_state().get_events_by_status("AVAILABLE")
    for event in available_events:
        for condition in event.activation_conditions:
            if isinstance(condition, CharacterInteractionOption):
                if condition.id == activation_condition_id:
                    game_state.events.get_state().start_event(event.id, condition.id)
                    return event
    return None

def move_player(scenario_id: str, from_checkpoint_id: str) -> ActionResponse:
    try:
        game_state = SimulatedGameStateSingleton.get_instance()
        player = game_state.read_only_characters.get_player()
        if not player:
            raise Exception("Player not found in game state.")
        game_state.map.place_character(player,scenario_id)
        changeset = get_incremental_changes(from_checkpoint_id)

        #check if any event triggered

        triggered_event = check_and_start_event_triggers(game_state)
        
        if triggered_event:
            follow_up = FollowUpAction(
                type=FollowUpActionType.START_NARRATIVE_STREAM,
                payload=StartNarrativeStreamPayload(event_id=triggered_event.id)
            )
        else:
            follow_up = FollowUpAction(type=FollowUpActionType.NONE, payload=None)
            
        # Return the complete, successful response.
        return ActionResponse(changeset=changeset, follow_up_action=follow_up)


    except Exception as e:
        return ActionResponse(
            changeset={},
            follow_up_action=FollowUpAction(type=FollowUpActionType.NONE),
            error=str(e)
        )

def trigger_character_activation_condition(activation_condition_id: str, from_checkpoint_id: str) -> ActionResponse:
    try:
        game_state = SimulatedGameStateSingleton.get_instance()
        changeset = get_incremental_changes(from_checkpoint_id)

        triggered_event = _try_start_character_activation_condition_event(game_state, activation_condition_id)
        
        if triggered_event:
            follow_up = FollowUpAction(
                type=FollowUpActionType.START_NARRATIVE_STREAM,
                payload=StartNarrativeStreamPayload(event_id=triggered_event.id)
            )
        else:
            follow_up = FollowUpAction(type=FollowUpActionType.NONE, payload=None)
            
        # Return the complete, successful response.
        return ActionResponse(changeset=changeset, follow_up_action=follow_up)


    except Exception as e:
        return ActionResponse(
            changeset={},
            follow_up_action=FollowUpAction(type=FollowUpActionType.NONE),
            error=str(e)
        )