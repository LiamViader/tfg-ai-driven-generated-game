from langgraph.graph import StateGraph, END
from langchain_core.runnables import Runnable
from subsystems.image_generation.characters.create.schemas import GraphState
from subsystems.image_generation.characters.create.nodes import process_all_characters_node


def get_created_character_images_generation_app() -> Runnable:
    builder = StateGraph(GraphState)
    builder.add_node("process_all_characters", process_all_characters_node)
    builder.set_entry_point("process_all_characters")
    builder.add_edge("process_all_characters", END)
    return builder.compile()
