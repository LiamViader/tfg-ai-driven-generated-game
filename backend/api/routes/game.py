from fastapi import APIRouter, HTTPException
from api.services import generator

router = APIRouter()

@router.post("/generate")
def launch_generation(user_prompt: str = "About cars that are alive."):
    return generator.start_generation(user_prompt)
