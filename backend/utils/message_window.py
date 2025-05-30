from typing import List, Any, Sequence # Puedes reemplazar Any con BaseMessage si lo tienes importado
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage 

def get_valid_messages_window(
    all_messages: Sequence[BaseMessage], # Lista completa de mensajes (objetos tipo BaseMessage)
    n_last_messages: int
) -> Sequence[BaseMessage]:
    """
    Truncates the message list to the most recent n_last_messages,
    ensuring the validity of tool call sequences.
    May return up to n_last_messages + 1 (if a parent AIMessage is added)
    or fewer if messages are removed to maintain validity.
    """
    if not all_messages:
        return []

    if n_last_messages <= 0:
        return [] 
    
    if n_last_messages>=len(all_messages):
        return all_messages

    candidate_messages = all_messages[-n_last_messages:]

    first_message_in_slice = candidate_messages[0]
    if isinstance(first_message_in_slice, ToolMessage):
        original_slice_start_index = len(all_messages) - len(candidate_messages) 
        while original_slice_start_index>=0 and isinstance(all_messages[original_slice_start_index], ToolMessage): 
            original_slice_start_index-=1
        return all_messages[original_slice_start_index:]
    else:
        return candidate_messages
            