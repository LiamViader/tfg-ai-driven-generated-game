from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from typing import Annotated, Dict, Any
from pydantic import BaseModel, Field
from subsystems.generation.refinement_loop.constants import AgentName

class InjectedToolContext(BaseModel):
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")] = Field(..., description="Field name in the state where tool-generated messages should be appended (e.g., 'map_executor_messages').")
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")] = Field(..., description="Field name in the state where the tool should append operation logs.")
    tool_call_id: Annotated[str, InjectedToolCallId] = Field(..., description="Unique identifier for the current tool call, used for linking messages to tool executions.")

class ToolLog(BaseModel):
    tool_called: str = Field(..., description="Name of the toool called")
    args: Dict[str, Any] = Field(..., description="Args for the tool call")
    is_query: bool = Field(..., description="Flag indicating whether the tool is a query tool")
    message: str = Field(..., description="Message returned by the tool")
    success: bool = Field(..., description="Whether the operation of the tool succeeded")

class ClearLogs:
    """Centinel class to indicate the logs must be cleared."""
    pass


class AgentLog(BaseModel):
    agent_name: AgentName = Field(default=AgentName.MAP, description="Name of the agent that produced this log")
    summary: str = Field(default="", description="Summarized log of the agent's operations")