from typing import Dict, List, Optional, Any, Annotated, Sequence, Literal, Set
from pydantic import BaseModel, Field
from copy import deepcopy
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
import operator
# El '.' significa "desde el directori actual (schemas)"
from core_game.map.schemas import ScenarioModel, Direction, OppositeDirections
from core_game.map.schemas import GameMapModel


class SummarizeGraphState(BaseModel):




    #shared with all other agents
    logs_field_to_update:  str = Field(default="logs", description="Name of the field in the state where tool-generated logs should be appended")
    messages_field_to_update: str = Field(default="messages", description="Name of the field in the state where tool-generated messages should be appended")
    logs_to_summarize: Sequence[Dict[str, Any]] = Field(default_factory=list, description="list of the logs the sumarize agent has to summarize")
