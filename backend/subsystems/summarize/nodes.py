from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
import json
from langgraph.prebuilt import ToolNode
from typing import Sequence, Dict, Any, List
from subsystems.summarize.schemas.graph_state import SummarizeGraphState

from subsystems.agents.utils.logs import ToolLog
from subsystems.summarize.prompts.summarize_operations import format_summarize_log_operations_prompt

def receive_operations_log_node(state: SummarizeGraphState):
    """
    First node of the graph.
    Entry point, any preprocess will happen here.
    """

    print("---ENTERING: RECEIVE OPERATIONS LOG NODE---")

    return {}

def summarize_operations_node(state: SummarizeGraphState):

    def format_operation_logs(operation_logs: Sequence[ToolLog]):
        successful_operations = []
        for operation in operation_logs:
            if operation.success and not operation.is_query:
                op_dict = {
                    "tool_called": operation.tool_called,
                    "arguments": operation.args,
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
        "sumarized_operations_result": summary
    }