from langgraph.graph import StateGraph, END
from .schemas import CharacterProcessorState
from .nodes import generate_prompt_for_character, generate_image_from_prompt, increment_retry_generate_character_prompt, posprocess_generated_image, increment_retry_analize_facing_dir

MAX_RETRIES = 2

def should_retry_prompt(state: CharacterProcessorState) -> str:
    if not state.error:
        return "generate_image"
    if state.retry_character_prompt_count < MAX_RETRIES:
        return "retry"
    return "fail"

def check_image_generation_success(state: CharacterProcessorState) -> str:
    """
    Conditional check to determine if the image generation was successful or if it failed.
    """
    if not state.error:
        return "postprocess_image"
    
    return "fail"

def should_retry_postprocess(state: CharacterProcessorState) -> str:
    """
    Conditional check to determine if the post-processing of the image should be retried.
    """
    if not state.error:
        return "end"
    
    if state.retry_analize_facing_dir_count < MAX_RETRIES:
        return "retry"
    
    return "fail"


def get_character_processor_graph_app():
    builder = StateGraph(CharacterProcessorState)

    builder.add_node("generate_prompt", generate_prompt_for_character)
    builder.add_node("generate_image", generate_image_from_prompt)
    builder.add_node("postprocess_image", posprocess_generated_image)
    builder.add_node("increment_retries_character_prompt", increment_retry_generate_character_prompt)
    builder.add_node("increment_retry_analize_facing_dir", increment_retry_analize_facing_dir)

    builder.set_entry_point("generate_prompt")

    builder.add_conditional_edges(
        "generate_prompt",
        should_retry_prompt,
        {
            "generate_image": "generate_image",
            "retry": "increment_retries_character_prompt",
            "fail": END,
        },
    )

    builder.add_edge("increment_retries_character_prompt", "generate_prompt")
    builder.add_conditional_edges(
        "generate_image",
        check_image_generation_success,
        {
            "postprocess_image": "postprocess_image",
            "fail": END,
        },
    )
    builder.add_conditional_edges(
        "postprocess_image",
        should_retry_postprocess,
        {
            "end": END,
            "retry": "increment_retry_analize_facing_dir",
            "fail": END,
        },
    )
    builder.add_edge("increment_retry_analize_facing_dir", "postprocess_image")
    return builder.compile()
