from langchain_core.tools import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from typing import Annotated
from pydantic import BaseModel, Field

class InjectedToolContext(BaseModel):
    messages_field_to_update: Annotated[str, InjectedState("messages_field_to_update")] = Field(..., description="Field name in the state where tool-generated messages should be appended (e.g., 'map_executor_messages').")
    logs_field_to_update: Annotated[str, InjectedState("logs_field_to_update")] = Field(..., description="Field name in the state where the tool should append operation logs.")
    tool_call_id: Annotated[str, InjectedToolCallId] = Field(..., description="Unique identifier for the current tool call, used for linking messages to tool executions.")