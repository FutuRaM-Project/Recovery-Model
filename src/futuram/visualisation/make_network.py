import networkx as nx
import matplotlib.pyplot as plt

def make_network_processs(model):
    """
    Makes a network of the processes in the model.
    Uses the networkx package to make a directed graph of the processes and flows in the model.
    """

    # Create a new directed graph
    G = nx.DiGraph()

    # make color dictionary
    transformation_levels = set([process.transformation_level for process in model.processes.values()])

    colours = plt.rcParams['axes.prop_cycle'].by_key()['color']

    color_dict = {transformation_level: colours[i] for i, transformation_level in enumerate(transformation_levels)}

    # Add nodes for each process and material in the model
    for process in model.processes.values():
        G.add_node(process.name, color=color_dict[process.transformation_level], type='process')

    # Add edges for each flow in the model
    for flow in model.get_flows().values():
        G.add_edge(flow.process_from, flow.process_to, amount=flow.amount)

    # Change the label of each node to replace underscores with newlines
    labels = { node: node.replace('_', '\n') for node in G.nodes }
    nx.set_node_attributes(G, labels, 'label')

    # Draw the network
    pos = nx.circular_layout(G)
    node_colors = [data['color'] for _, data in G.nodes(data=True)]  # Extract the 'color' attribute from node data
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=6, font_family='sans-serif', labels=nx.get_node_attributes(G, 'label'))
    nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'amount'), font_size=4, font_family='sans-serif')


    plt.title('FutuRaM recovery model: process network')



    # Show the plot
    plt.axis('off')
    plt.show()
    plt.savefig(f'../figures/{model.name}_process_network.pdf')
    print(f'Process network figure saved to ../figures/{model.name}_process_network.pdf')

