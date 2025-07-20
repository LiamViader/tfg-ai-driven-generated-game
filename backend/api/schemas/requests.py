from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    user_prompt: str = Field(default="Improvise")