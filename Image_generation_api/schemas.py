from pydantic import BaseModel

class GenerationRequest(BaseModel):
    scene_summary: str
    scene_detail: str
    ground_detail: str
    ground_summary: str
    graphic_style: str