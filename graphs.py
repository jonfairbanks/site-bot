import matplotlib.pyplot as plt
from graphviz import Digraph

def shorten_url(url):
    """Shorten a URL by dropping the middle."""
    if len(url) <= 20:
        return url
    parts = url.split('/')
    if len(parts) <= 3:
        return url
    return f"{parts[0]}/{parts[1]}/.../{parts[-1]}"


def generate_history_graph(HISTORY, filename):
    try:
        # Save history graph
        urls = [shorten_url(h[0]) for h in HISTORY]
        times = [h[1] for h in HISTORY]
        img_length = len(HISTORY) * 0.25
        fig, ax = plt.subplots(figsize=(25, img_length))
        fig.subplots_adjust(top=0.98, bottom=0.025)
        ax.barh(urls, times, align="center")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("URLs")
        ax.set_title("Request Time History")

        # Reduce font size and rotate Y-axis tick labels
        ax.tick_params(axis="y", labelsize=8, rotation=45)

        plt.savefig(f"{filename}.png")
        print(f"** {filename}.png saved! **")
    except Exception as e:
        print(f"Error creating history graph: {e}")

    return


def generate_waterfall(HISTORY, filename):
    graph = Digraph(format="png")

    # Add nodes to graph
    try:
        for i, (url, _) in enumerate(HISTORY):
            graph.node(str(i), url)
    except:
        print("Add nodes failed")

    # Add edges to graph
    try:
        for i in range(1, len(HISTORY)):
            graph.edge(str(i - 1), str(i))
    except:
        print("Add edges failed")

    # Render the graph
    try:
        graph.render(str(f"{filename}"), view=False, cleanup=True)
        print(f"** {filename}.png saved! **")
    except:
        print("Rendering waterfall failed")
    return
