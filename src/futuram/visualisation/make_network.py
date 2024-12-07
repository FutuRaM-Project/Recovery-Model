"""
make_network.py

This module contains functions for creating network graphs of processes and matter in a model.

Functions:
- make_network(model):  This is a wrapper function that calls one of the subroutines.
- make_network_matter(model): Makes a network of the matter in the model.
- make_network_process(model): Makes a network of the processes in the model.

Dependencies:
- networkx
- matplotlib

"""
import os
import networkx as nx
import matplotlib.pyplot as plt

# Create a new directed graph
G = nx.DiGraph()


def make_network(model):
    """
    This is a wrapper function that calls either make_network_process or make_network_matter depending on the type of object.
    """
    if not os.path.isdir('../figures/networks/'):
        os.mkdir('../figures/networks/')

    if model.type == "model":
        make_network_process(model)
    elif model.type == "matter":
        make_network_matter(model)
    else:
        print("Object not supported. Only matter and process models are supported.")


# TODO: make this function
def make_network_matter(model):
    """
    Makes a network of the matter in the model.
    Uses the networkx package to make a graph of the matter composition at all levels in the model.
    """
    # Create a new directed graph


def make_network_process(model):
    """
    Makes a network of the processes in the model.
    Uses the networkx package to make a directed graph of the processes and flows in the model.
    """

    print(f"\n\n{'='*90}\n\t Making process network for model: {model.name}\n{'='*90}\n")

    # Create a new directed graph
    G = nx.DiGraph()

    # make color dictionary
    transformation_levels = set(
        [process.transformation_level for process in model.processes.values()]
    )

    colours = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    color_dict = {
        transformation_level: colours[i]
        for i, transformation_level in enumerate(transformation_levels)
    }

    # Add nodes for each process and material in the model
    for process in model.processes.values():
        G.add_node(
            process.name, color=color_dict[process.transformation_level], type="process"
        )

    # Add edges for each flow in the model
    for flow in model.get_flows().values():
        G.add_edge(flow.process_from, flow.process_to, amount=flow.amount)

    # Change the label of each node to replace underscores with newlines
    labels = {node: node.replace("_", "\n") for node in G.nodes}
    nx.set_node_attributes(G, labels, "label")

    # Draw the network
    pos = nx.circular_layout(G)
    node_colors = [
        data["color"] for _, data in G.nodes(data=True)
    ]  # Extract the 'color' attribute from node data
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)
    nx.draw_networkx_edges(G, pos, edge_color="gray")
    nx.draw_networkx_labels(
        G,
        pos,
        font_size=6,
        font_family="sans-serif",
        labels=nx.get_node_attributes(G, "label"),
    )
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=nx.get_edge_attributes(G, "amount"),
        font_size=4,
        font_family="sans-serif",
    )

    plt.title("FutuRaM recovery model: process network")

    # Show the plot
    plt.axis("off")
    plt.savefig(f"../figures/networks/{model.name}_process_network.png", format="png", dpi=600)
    plt.savefig(f"../figures/networks/{model.name}_process_network.svg", format="svg")
    plt.savefig(f"../figures/networks/{model.name}_process_network.pdf", format="pdf")
    print(
        f"Process network figure saved to ../figures/{model.name}_process_network.pdf\n"
    )
