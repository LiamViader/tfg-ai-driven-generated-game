from typing import Dict, List, Optional, Any, Annotated, Sequence, Literal, Set
from pydantic import BaseModel, Field
import operator
from  subsystems.agents.utils.logs import ToolLog
from subsystems.agents.utils.schemas import AgentLog
from subsystems.generation.refinement_loop.constants import AgentName

class SummarizeLogsGraphState(BaseModel):
    operations_log_to_summarize: Sequence[ToolLog] = Field(default_factory=list, description="list of the operations the sumarize agent has to summarize")

    current_agent_name: AgentName = Field(default=AgentName.MAP, description="Name of the agent whose log is being summarized")

    sumarized_operations_result: AgentLog = Field(default_factory=AgentLog, description="Output summary of the operations to summarize")


