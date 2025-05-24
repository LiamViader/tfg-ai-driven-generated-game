from langgraph.graph import StateGraph, END

from ..schemas.graph_state import MapGraphState
from .nodes import receive_objective_node
# Más adelante importarás los otros nodos aquí (plan_map_changes_node, etc.)

# --- Define aquí temporalmente los otros nodos como placeholders para que el grafo compile ---
# --- Deberás reemplazarlos con sus implementaciones reales ---
def plan_map_changes_node_placeholder(state: MapGraphState) -> MapGraphState:
    print("---NODE: Plan Map Changes (Placeholder)---")
    # Lógica del AgenteRazonadorDeMapas para crear un plan
    # ...
    # Actualiza state.proposed_plan, state.plan_justification
    # Ejemplo:
    state.proposed_plan = [{"action": "create_scenario", "details": {"name": "Placeholder Scenario"}}]
    state.plan_justification = "Plan de placeholder para continuar el flujo."
    print(f"Proposed plan: {state.proposed_plan}")
    return state

# (Define placeholders similares para validate_plan_outcome_node, etc. para poder definir el flujo)
# ...

def get_map_generation_graph():
    """
    Construye y compila el grafo LangGraph para la generación de mapas.
    """
    # Define el grafo de estado, especificando el objeto de estado Pydantic
    # Esto permite que los nodos reciban y devuelvan directamente instancias de MapGraphState
    graph_builder = StateGraph(MapGraphState)

    # Añade los nodos al grafo
    graph_builder.add_node("receive_objective", receive_objective_node)
    graph_builder.add_node("plan_map_changes", plan_map_changes_node_placeholder) # Usa el placeholder por ahora
    # ... (añade los otros nodos aquí: validate_plan, apply_plan, etc.)

    # Establece el punto de entrada del grafo
    graph_builder.set_entry_point("receive_objective")

    # Define las transiciones (aristas) entre nodos
    graph_builder.add_edge("receive_objective", "plan_map_changes")
    # ... (define el resto de las transiciones y aristas condicionales aquí)
    # Ejemplo de cómo terminaría (simplificado):
    graph_builder.add_edge("plan_map_changes", END) # Temporalmente, hasta que tengas más nodos

    # Compila el grafo
    map_generation_graph = graph_builder.compile()
    return map_generation_graph

# Esto es útil para probar este módulo directamente
if __name__ == "__main__":
    # Crea una instancia del grafo
    map_graph = get_map_generation_graph()

    # Ejemplo de cómo invocarías el grafo (esto iría en tu service.py o main_orchestrator.py)
    initial_input_data = {
        "current_objective": "Generar un pequeño pueblo de inicio con una plaza y una tienda.",
        "global_narrative_context": "Es un mundo de fantasía medieval pacífico, al borde de un bosque antiguo.",
        "game_rules_and_constraints": [
            "Los pueblos deben tener al menos una fuente de agua.",
            "Las tiendas suelen estar en la plaza principal o cerca."
        ],
        # "initial_scenarios": {} # Opcional, si empiezas con algo
    }

    # Para invocar el grafo (en un entorno asíncrono normalmente usarías ainvoke)
    # El resultado final contendrá el MapGraphState después de que el grafo termine.
    # Como hemos puesto un END temporal, terminará rápido.
    final_state = map_graph.invoke(initial_input_data)
    
    print("\n---FINAL GRAPH STATE---")
    if final_state:
        # Si MapGraphState es devuelto directamente (típico en invoke con grafos tipados)
        print(final_state.model_dump_json(indent=2) if hasattr(final_state, 'model_dump_json') else final_state)
        # Si es una lista de estados (como a veces con stream), toma el último.
        # final_state_obj = final_state[-1] if isinstance(final_state, list) else final_state
        # print(final_state_obj.model_dump_json(indent=2))