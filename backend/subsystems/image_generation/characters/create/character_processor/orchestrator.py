from langgraph.graph import StateGraph, END
from .schemas import CharacterProcessorState
from .nodes import generate_prompt_for_character, generate_image_from_prompt, increment_retry_counter

MAX_RETRIES = 2

def should_retry_prompt(state: CharacterProcessorState) -> str:
    if not state.error:
        return "generate_image"
    if state.retry_count < MAX_RETRIES:
        return "retry"
    return "fail"

def get_character_processor_graph_app():
    builder = StateGraph(CharacterProcessorState)

    builder.add_node("generate_prompt", generate_prompt_for_character)
    builder.add_node("generate_image", generate_image_from_prompt)
    builder.add_node("increment_retries", increment_retry_counter)

    builder.set_entry_point("generate_prompt")

    builder.add_conditional_edges(
        "generate_prompt",
        should_retry_prompt,
        {
            "generate_image": "generate_image",
            "retry": "increment_retries",
            "fail": END,
        },
    )

    builder.add_edge("increment_retries", "generate_prompt")
    builder.add_edge("generate_image", END)

    return builder.compile()
