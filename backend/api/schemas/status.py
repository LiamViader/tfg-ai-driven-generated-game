from pydantic import BaseModel
from typing import Literal

StatusType = Literal["idle", "running", "done", "error", "started"]
class GenerationStatusModel(BaseModel):
    status: StatusType
    progress: float
    message: str
    detail: str
