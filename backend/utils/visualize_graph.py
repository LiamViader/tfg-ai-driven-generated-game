import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy

from subsystems.map.schemas.simulated_map import SimulatedMapModel

def visualize_map_graph(simulated_map: SimulatedMapModel):
    """
    Visualiza el grafo de escenarios usando NetworkX y Matplotlib.
    """
    if not simulated_map.simulated_scenarios:
        print("No hay escenarios para visualizar.")
        return

    G = nx.DiGraph()  # Usamos un grafo dirigido ya que las salidas tienen una dirección

    # Añadir nodos
    for scenario_id, scenario in simulated_map.simulated_scenarios.items():
        # Usar getattr para más seguridad si algún atributo pudiera faltar
        zone = getattr(scenario, 'zone', 'N/A')
        indoor_outdoor = getattr(scenario, 'indoor_or_outdoor', 'N/A')
        visual_desc = getattr(scenario, 'visual_description', 'N/A')
        narrative_ctx = getattr(scenario, 'narrative_context', 'N/A')
        
        # Considera truncar visual_desc y narrative_ctx si son muy largos para la visualización
        # Ejemplo:
        # visual_desc_display = (visual_desc[:37] + '...') if len(visual_desc) > 40 else visual_desc
        # narrative_ctx_display = (narrative_ctx[:37] + '...') if len(narrative_ctx) > 40 else narrative_ctx

        G.add_node(scenario_id, name=scenario.name, 
                   label=f"{scenario.name}\n({scenario_id})\nZone: {zone}\nIndoor/Outdoor: {indoor_outdoor}\nVisual: {visual_desc}\nNarrative: {narrative_ctx}")

    # Añadir aristas (conexiones)
    edge_labels = {}
    for scenario_id, scenario in simulated_map.simulated_scenarios.items():
        for direction, exit_info in scenario.exits.items():
            if exit_info and exit_info.target_scenario_id in simulated_map.simulated_scenarios:
                G.add_edge(scenario_id, exit_info.target_scenario_id)
                edge_labels[(scenario_id, exit_info.target_scenario_id)] = f"{direction}\n({exit_info.connection_type})"
            elif exit_info:
                print(f"Advertencia: El escenario '{scenario_id}' tiene una salida a un escenario no existente '{exit_info.target_scenario_id}'.")

    if not G.nodes():
        print("Grafo vacío después de procesar escenarios.")
        return

    plt.figure(figsize=(16, 12)) # Un poco más grande por si hay mucho texto
    
    try:
        pos = nx.spring_layout(G, k=1.2, iterations=50, seed=42) # Ajustar k y añadir seed para reproducibilidad
    except Exception: 
        pos = nx.kamada_kawai_layout(G)

    node_labels_from_graph = {node: data['label'] for node, data in G.nodes(data=True)}
    # Ajusta node_size y font_size según necesites
    nx.draw_networkx_nodes(G, pos, node_size=3500, node_color="skyblue", alpha=0.9)
    
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle="->", arrowsize=20, 
                           edge_color="gray", alpha=0.7, node_size=3500) 
    
    nx.draw_networkx_labels(G, pos, labels=node_labels_from_graph, font_size=7) # Fuente más pequeña para nodos

    # --- ¡AQUÍ AÑADES LAS ETIQUETAS DE LAS ARISTAS! ---
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_color='red', # Puedes cambiar el color para distinguirlas
        font_size=6,      # Ajusta el tamaño de la fuente
        # rotate=False,   # Para evitar que las etiquetas roten con el ángulo de la arista
        # label_pos=0.3   # Ajusta la posición de la etiqueta a lo largo de la arista (0=origen, 0.5=medio, 1=destino)
    )
    # ----------------------------------------------------

    plt.title("Visualización del Mapa de Escenarios", fontsize=16)
    plt.axis('off') 
    plt.tight_layout()
    plt.show()