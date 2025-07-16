from fastapi import APIRouter, HTTPException, Query
from api.services import generator
from api.services.generation_status import get_status
from api.schemas.status import GenerationStatusModel
from api.services import game_state

router = APIRouter()

@router.post("/generate", response_model=GenerationStatusModel)
def launch_generation(user_prompt: str = "Improvise"):
    print("SADDS")
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