import networkx as nx
import matplotlib.pyplot as plt

from typing import Optional

from core_game.game_state.domain import GameState
from core_game.game_state.singleton import GameStateSingleton


def visualize_map_graph(game_state: Optional[GameState] = None) -> None:
    """Display the current map graph using NetworkX and Matplotlib.

    Parameters
    ----------
    game_state:
        The :class:`GameState` instance to visualize. If ``None`` (default),
        the current instance provided by :class:`GameStateSingleton` will be
        used.
    """

    if game_state is None:
        game_state = GameStateSingleton.get_instance()

    game_map_model = game_state.game_map.to_model()
    scenarios = game_map_model.scenarios
    connections = game_map_model.connections

    if not scenarios:
        print("No hay escenarios para visualizar.")
        return

    G = nx.DiGraph()

    for scenario_id, scenario in scenarios.items():
        zone = getattr(scenario, "zone", "N/A")
        indoor_outdoor = getattr(scenario, "indoor_or_outdoor", "N/A")
        visual_desc = getattr(scenario, "visual_description", "N/A")
        narrative_ctx = getattr(scenario, "narrative_context", "N/A")

        G.add_node(
            scenario_id,
            name=scenario.name,
            label=(
                f"{scenario.name}\n({scenario_id})\nZone: {zone}\n"
                f"Indoor/Outdoor: {indoor_outdoor}\nVisual: {visual_desc}\n"
                f"Narrative: {narrative_ctx}"
            ),
        )

    edge_labels = {}
    for scenario_id, scenario in scenarios.items():
        for direction, conn_id in scenario.connections.items():
            if not conn_id:
                continue
            conn = connections.get(conn_id)
            if not conn:
                continue
            target_id = conn.scenario_b_id if conn.scenario_a_id == scenario_id else conn.scenario_a_id
            if target_id in scenarios:
                G.add_edge(scenario_id, target_id)
                edge_labels[(scenario_id, target_id)] = f"{direction}\n({conn.connection_type})"
            else:
                print(
                    f"Advertencia: El escenario '{scenario_id}' tiene una conexión a un escenario no existente '{target_id}'."
                )

    if not G.nodes():
        print("Grafo vacío después de procesar escenarios.")
        return

    plt.figure(figsize=(16, 12))

    try:
        pos = nx.spring_layout(G, k=1.2, iterations=50, seed=42)
    except Exception:
        pos = nx.kamada_kawai_layout(G)

    node_labels_from_graph = {node: data["label"] for node, data in G.nodes(data=True)}

    nx.draw_networkx_nodes(G, pos, node_size=3500, node_color="skyblue", alpha=0.9)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=G.edges(),
        arrowstyle="->",
        arrowsize=20,
        edge_color="gray",
        alpha=0.7,
        node_size=3500,
    )
    nx.draw_networkx_labels(G, pos, labels=node_labels_from_graph, font_size=7)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="red", font_size=6)

    plt.title("Visualización del Mapa de Escenarios", fontsize=16)
    plt.axis("off")
    plt.tight_layout()
    plt.show()
