from fastapi import APIRouter, HTTPException, Query
from api.services import generator
from api.services.generation_status import get_status
from api.services.actions import move_player, trigger_character_activation_condition
from api.schemas.status import GenerationStatusModel
from api.services import game_state
from api.schemas.requests import GenerationRequest, ActionRequest, ActionType
from api.schemas.responses import ActionResponse, FollowUpAction, FollowUpActionType
from fastapi.responses import StreamingResponse
from api.services.narrative_streamer import generate_narrative_stream
router = APIRouter()

@router.post("/generate", response_model=GenerationStatusModel)
def launch_generation(payload: GenerationRequest):
    user_prompt = payload.user_prompt
    if get_status().status == "running":
        raise HTTPException(status_code=400, detail="A generation is already in progress")
    return generator.start_generation(user_prompt)

@router.get("/generate/status", response_model=GenerationStatusModel)
def generation_status():
    return generator.get_generation_status()

@router.get("/state/full")
def get_full_state():
    status = get_status().status

    if status == "running":
        raise HTTPException(status_code=409, detail="Game state is still being generated")
    if status == "error":
        raise HTTPException(status_code=500, detail="Generation failed. No valid game state available")
    
    return game_state.get_full_game_state()

@router.get("/state/changes")
def get_incremental_changes(from_checkpoint: str = Query(..., description="ID of the checkpoint to diff from")):
    status = get_status().status

    if status == "running":
        raise HTTPException(status_code=409, detail="Game state is still being generated")
    if status == "error":
        raise HTTPException(status_code=500, detail="Generation failed. No valid game state available")
    
    return game_state.get_incremental_changes(from_checkpoint)

@router.post("/action", response_model=ActionResponse)
def perform_game_action(action_request: ActionRequest):
    """
    Unified endpoint to process any player action.
    Returns state changes and the next action for the client to perform.
    """
    action_type = action_request.action_type
    payload = action_request.payload
    from_checkpoint_id = action_request.from_checkpoint_id
    
    # You would use 'from_checkpoint_id' here to call your logic
    # that generates the incremental changeset. For example:
    # changeset = game_state.get_incremental_changes_from_action(from_checkpoint_id, action_request)
    
    print(f"Action '{action_type.value}' received from checkpoint '{from_checkpoint_id}'")

    # Example logic for different actions
    if action_type == ActionType.MOVE_PLAYER:
        if not payload.new_scenario_id:
            raise HTTPException(
                status_code=422, 
                detail="Field 'new_scenario_id' is required for a 'MOVE_PLAYER' action."
            )
        return move_player(payload.new_scenario_id, from_checkpoint_id)

    elif action_type == ActionType.TRIGGER_EVENT:
        if not payload.activation_condition_id:
            raise HTTPException(
                status_code=422, 
                detail="Field 'activation_condition_id' is required for a 'TRIGGER_EVENT' action."
            )
        return trigger_character_activation_condition(payload.activation_condition_id, from_checkpoint_id)

    else:
        raise HTTPException(
            status_code=422, 
            detail="Action type not found."
        )
    
@router.get("/event/stream/{event_id}", tags=["Game Events"])
async def stream_narrative_event(event_id: str):
    """
    Initiates a streaming connection (Server-Sent Events) for a narrative event.
    Sends dialogue/action fragments in real-time.
    """
    # Delegates all logic to the generator we created in the service.
    return StreamingResponse(generate_narrative_stream(event_id), media_type="text/event-stream")