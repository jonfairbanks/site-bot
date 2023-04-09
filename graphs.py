import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def shorten_url(url):
    """Shorten a URL by dropping the middle."""
    if len(url) <= 30:
        return url
    parts = url.split("/")
    if len(parts) <= 3:
        return url
    return f"{parts[0]}/{parts[1]}/.../{parts[-1]}"


def generate_latency_graph(HISTORY, filename):
    try:
        # Save history graph
        urls = [shorten_url(h[0]) for h in HISTORY]
        times = [h[1] for h in HISTORY]
        img_length = len(HISTORY) + 1
        fig, ax = plt.subplots(figsize=(25, img_length))
        # fig.subplots_adjust(top=0.98, bottom=0.025)
        ax.barh(urls, times, align="center")
        ax.set_xlabel("Latency (sec)")
        ax.set_ylabel("Outbound URLs")
        ax.set_title("Outbound Request Latency")

        # Reduce font size and rotate Y-axis tick labels
        ax.tick_params(axis="y", labelsize=8, rotation=45)

        plt.savefig(f"{filename}.png")
        print(f"** {filename}.png saved! **")
    except Exception as e:
        print(f"Error creating history graph: {e}")

    return


def visualize_urls(data, filename):
    G = nx.DiGraph()
    for source, targets in data.items():
        G.add_node(source)
        for target in targets:
            G.add_edge(source, target)

    pos = nx.spring_layout(G, k=0.3)

    fig, ax = plt.subplots(figsize=(50, 50))
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500)
    nx.draw_networkx_edges(G, pos, ax=ax, width=1, edge_color="gray")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)
    ax.set_axis_off()

    filename = f"{filename}.png"
    plt.savefig(filename, bbox_inches="tight")
    print(f"** {filename} saved! **")


# def visualize_urls(data, ego_node, filename):
#     G = nx.Graph()
#     G.add_node(ego_node)
#     for source, targets in data.items():
#         if source == ego_node:
#             for target in targets:
#                 G.add_edge(source, target)
#         elif ego_node in targets:
#             G.add_edge(source, ego_node)

#     pos = nx.spring_layout(G, k=0.3)

#     fig, ax = plt.subplots(figsize=(50, 50))
#     nx.draw_networkx_nodes(G, pos, ax=ax, node_size=500)
#     nx.draw_networkx_edges(G, pos, ax=ax, width=1, edge_color="gray")
#     nx.draw_networkx_labels(G, pos, ax=ax, font_size=10)
#     ax.set_axis_off()

#     filename = f"{filename}.png"
#     plt.savefig(filename, bbox_inches="tight")
#     print(f"** {filename} saved! **")
