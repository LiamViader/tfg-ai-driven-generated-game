from typing import Dict, List, Optional, Any, Annotated, Sequence, Literal, Set
from pydantic import BaseModel, Field
import operator
from  subsystems.agents.utils.logs import ToolLog

class SummarizeLogsGraphState(BaseModel):
    operations_log_to_summarize: Sequence[ToolLog] = Field(default_factory=list, description="list of the operations the sumarize agent has to summarize")

    #shared with other agents
    sumarized_operations_result: str = Field(default="", description="Output summary of the operations to summarize")

    refinement_pass_changelog: Annotated[Sequence[str], operator.add] = Field(
        default_factory=list,
        description="A log that accumulates the summary or outcome of each agent's operation in every pass."
    )

