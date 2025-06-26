from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
import json
from langgraph.prebuilt import ToolNode
from typing import Sequence, Dict, Any, List
from subsystems.summarize_agent_logs.schemas.graph_state import SummarizeLogsGraphState

from subsystems.agents.utils.logs import ToolLog
from subsystems.summarize_agent_logs.prompts.summarize_operations import format_summarize_log_operations_prompt

def receive_operations_log_node(state: SummarizeLogsGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OPERATIONS LOG NODE---")

    return {}

def summarize_operations_node(state: SummarizeLogsGraphState):

    def convert_to_json_serializable(item: Any) -> Any:
        """
        Recursively converts Pydantic models and other non-serializable objects
        into a format that can be handled by json.dumps.
        """
        if hasattr(item, 'model_dump'):  # Para Pydantic v2
            return item.model_dump()
        if hasattr(item, 'dict'):  # Para Pydantic v1
            return item.dict()
        if isinstance(item, dict):
            return {key: convert_to_json_serializable(value) for key, value in item.items()}
        if isinstance(item, list):
            return [convert_to_json_serializable(element) for element in item]
        # Si no es ninguno de los anteriores, se asume que es serializable
        return item

    def format_operation_logs(operation_logs: Sequence[ToolLog]):
        successful_operations = []
        for operation in operation_logs:
            if operation.success and not operation.is_query:
                op_dict = {
                    "tool_called": operation.tool_called,
                    "arguments": convert_to_json_serializable(operation.args),
                    "result_message": operation.message
                }
                successful_operations.append(op_dict)

        return json.dumps(successful_operations, indent=2)
    
    print("---ENTERING: SUMMARIZE OPERATIONS NODE---")

    formatted_operations = format_operation_logs(state.operations_log_to_summarize)

    summarizing_llm = ChatOpenAI(model="gpt-4.1-nano")

    prompt = format_summarize_log_operations_prompt(formatted_operations, 300)

    response = summarizing_llm.invoke(prompt)

    summary = response.content

    #falta fer validacio i tal del output del llm

    return {
        "sumarized_operations_result": summary,
        "refinement_pass_changelog": [summary]
    }