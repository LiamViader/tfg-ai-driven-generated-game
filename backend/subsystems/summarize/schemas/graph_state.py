from typing import Dict, List, Optional, Any, Annotated, Sequence, Literal, Set
from pydantic import BaseModel, Field
import operator
from  subsystems.agents.utils.logs import ToolLog

class SummarizeGraphState(BaseModel):
    operations_log_to_summarize: Sequence[ToolLog] = Field(default_factory=list, description="list of the operations the sumarize agent has to summarize")
    sumarized_operations_result: str = Field(default="", description="Output summary of the operations to summarize")


    #shared with all other agents
    logs_field_to_update:  str = Field(default="logs", description="Name of the field in the state where tool-generated logs should be appended")
    messages_field_to_update: str = Field(default="messages", description="Name of the field in the state where tool-generated messages should be appended")

