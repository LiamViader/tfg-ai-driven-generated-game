from typing import Literal
from api.schemas.status import GenerationStatusModel

# Dict for internal state
_current_status: dict = {
    "status": "idle",
    "progress": 0.0,
    "message": "Waiting to start generation...",
    "detail": "You can poll /generate/status to track progress"
}

def update_global_progress(global_progress: float, message: str = ""):
    _current_status["progress"] = global_progress
    _current_status["message"] = message

def set_done():
    _current_status["status"] = "done"
    _current_status["progress"] = 1.0
    _current_status["message"] = "Generation completed"

def set_error(message: str):
    _current_status["status"] = "error"
    _current_status["progress"] = 0.0
    _current_status["message"] = message

def reset():
    _current_status["status"] = "running"
    _current_status["progress"] = 0.0
    _current_status["message"] = "Starting generation..."

def get_status() -> GenerationStatusModel:
    return GenerationStatusModel(**_current_status)
