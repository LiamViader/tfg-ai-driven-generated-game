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
        G.add_node(scenario_id, name=scenario.name, label=f"{scenario.name}\n({scenario_id})")

    # Añadir aristas (conexiones)
    edge_labels = {}
    for scenario_id, scenario in simulated_map.simulated_scenarios.items():
        for direction, exit_info in scenario.exits.items():
            if exit_info and exit_info.target_scenario_id in simulated_map.simulated_scenarios:
                # Añadimos la arista
                G.add_edge(scenario_id, exit_info.target_scenario_id)
                # Guardamos información para la etiqueta de la arista
                edge_labels[(scenario_id, exit_info.target_scenario_id)] = f"{direction}\n({exit_info.connection_type})"
            elif exit_info:
                print(f"Advertencia: El escenario '{scenario_id}' tiene una salida a un escenario no existente '{exit_info.target_scenario_id}'.")


    if not G.nodes():
        print("Grafo vacío después de procesar escenarios.")
        return

    # Configuración de la visualización
    plt.figure(figsize=(14, 10))
    
    # Usar un layout que intente espaciar los nodos
    # Otros layouts: nx.spring_layout, nx.circular_layout, nx.shell_layout, etc.
    try:
        pos = nx.spring_layout(G, k=0.9, iterations=50) # k es la distancia óptima entre nodos
    except Exception: # Fallback por si spring_layout falla con grafos pequeños/desconectados
        pos = nx.kamada_kawai_layout(G)


    # Dibujar nodos
    node_labels = {node: data['label'] for node, data in G.nodes(data=True)}
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="skyblue", alpha=0.9)
    
    # Dibujar aristas
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrowstyle="->", arrowsize=20, 
                           edge_color="gray", alpha=0.7, node_size=3000) 
    
    # Dibujar etiquetas de nodos
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)

    plt.title("Visualización del Mapa de Escenarios", fontsize=15)
    plt.axis('off') # Ocultar ejes
    plt.tight_layout()
    plt.show()