

from langgraph.graph import StateGraph, END
from subsystems.image_generation.scenarios.create.scenario_processor.schemas import ScenarioProcessorState
from subsystems.image_generation.scenarios.create.scenario_processor.nodes import generate_payload_for_scenario, generate_image_from_payload, increment_retry_counter


MAX_RETRIES = 2

def should_retry_payload(state: ScenarioProcessorState) -> str:
    """
    Arista condicional. Decide si reintentar la generación de payload,
    continuar a la generación de imagen o terminar el flujo por un error.
    """
    if not state.error:
        return "generate_image"
    
    if state.retry_count < MAX_RETRIES:
        return "retry"
    
    return "fail"

def get_scenario_processor_graph_app():
    builder = StateGraph(ScenarioProcessorState)

    builder.add_node("generate_payload", generate_payload_for_scenario)
    builder.add_node("generate_image", generate_image_from_payload)
    builder.add_node("increment_retries", increment_retry_counter)

    builder.set_entry_point("generate_payload")


    builder.add_conditional_edges(
        "generate_payload",
        should_retry_payload,
        {
            "generate_image": "generate_image", 
            "retry": "increment_retries",        
            "fail": END                           
        }
    )

    builder.add_edge("increment_retries", "generate_payload")

    builder.add_edge("generate_image", END)

    return builder.compile()
